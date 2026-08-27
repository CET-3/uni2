from datetime import timedelta
from decimal import Decimal
from urllib.parse import urlparse

import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.db import IntegrityError
from django.test import override_settings
from django.utils import timezone

from asociados.models import (
    Asociado,
    CicloLectivo,
    Curso,
    LimiteSolicitudPublica,
    SolicitudAsociacion,
)
from asociados.services import (
    LimiteSolicitudExcedido,
    SolicitudAsociacionDuplicada,
    TransicionSolicitudInvalida,
    aprobar_datos_solicitud_asociacion,
    cancelar_solicitud_asociacion,
    completar_alta_solicitud_asociacion,
    consumir_limite_publico,
    corregir_solicitud_asociacion,
    crear_solicitud_asociacion,
    observar_solicitud_asociacion,
    rotar_token_seguimiento,
)
from auditoria.models import EventoAuditoria
from comunicaciones.models import Comunicacion, EntregaComunicacion
from comunicaciones.selectors import listar_entregas_para_origen
from cuotas.models import Cuota, PeriodoCuota


@pytest.fixture
def curso():
    return Curso.objects.create(
        anio="1ro",
        curso="1ra",
        division=Curso.DIVISION_CB,
        turno=Curso.TURNO_TM,
    )


def datos_solicitud(curso, **overrides):
    datos = {
        "nombre": "Ana",
        "apellido": "Flores",
        "dni": "48.123.456",
        "email": "ana@example.com",
        "telefono": "2995550192",
        "direccion": "Los Maitenes 142",
        "es_estudiante_cet3": True,
        "curso_actual": curso,
        "clasificacion_adherente": None,
    }
    datos.update(overrides)
    return datos


@pytest.fixture
def actor():
    return get_user_model().objects.create_user(
        username="operadora",
        first_name="María",
        last_name="Operadora",
    )


def crear_solicitud_directa(curso, *, estado=SolicitudAsociacion.ESTADO_RECIBIDA):
    return SolicitudAsociacion.objects.create(
        **datos_solicitud(curso),
        estado=estado,
        token_seguimiento_hash="d" * 64,
        token_seguimiento_vence_en=timezone.now() + timedelta(days=30),
    )


@pytest.mark.django_db(transaction=True)
@override_settings(
    UNI2_TRANSACTIONAL_EMAIL_MODE="enabled",
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    UNI2_SITE_URL="https://uni2.example",
)
def test_crear_solicitud_registra_auditoria_y_correo_sin_persistir_token(curso):
    solicitud = crear_solicitud_asociacion(
        datos=datos_solicitud(curso),
        actor_ip="203.0.113.10",
    )

    evento = EventoAuditoria.objects.get(
        entidad="asociados.SolicitudAsociacion",
        objeto_id=str(solicitud.pk),
    )
    entrega = listar_entregas_para_origen(
        "asociados.SolicitudAsociacion", solicitud.pk
    ).get()
    enlace = next(
        linea for linea in mail.outbox[0].body.splitlines() if linea.startswith("https://")
    )
    token = urlparse(enlace).path.rstrip("/").split("/")[-1]

    assert solicitud.estado == SolicitudAsociacion.ESTADO_RECIBIDA
    assert evento.origen == EventoAuditoria.ORIGEN_SITIO_PUBLICO
    assert evento.actor is None
    assert evento.actor_etiqueta == "Solicitante desde el sitio público"
    assert entrega.estado == EntregaComunicacion.ESTADO_ENVIADA
    assert Comunicacion.objects.count() == 1
    assert token not in solicitud.token_seguimiento_hash
    assert token not in str(evento.cambios)
    assert token not in str(Comunicacion.objects.values().get())


@pytest.mark.django_db
def test_crear_solicitud_rechaza_documento_de_asociado_aunque_tenga_formato(curso):
    Asociado.objects.create(
        nombre="Ana",
        apellido="Flores",
        dni="48.123.456",
        tipo=Asociado.TIPO_ASOCIADO,
        curso_actual=curso,
        fecha_alta=timezone.localdate(),
        fecha_inicio_cobro=timezone.localdate().replace(day=1),
    )

    with pytest.raises(SolicitudAsociacionDuplicada):
        crear_solicitud_asociacion(
            datos=datos_solicitud(curso, dni="48123456"),
            actor_ip="203.0.113.10",
        )

    contador = LimiteSolicitudPublica.objects.get(accion="crear_solicitud")
    assert contador.intentos == 1


@pytest.mark.django_db
def test_crear_solicitud_traduce_una_carrera_de_documento_duplicado(
    curso,
    monkeypatch,
):
    def simular_conflicto_de_unicidad(*args, **kwargs):
        raise IntegrityError("conflicto concurrente")

    monkeypatch.setattr(SolicitudAsociacion, "save", simular_conflicto_de_unicidad)

    with pytest.raises(SolicitudAsociacionDuplicada):
        crear_solicitud_asociacion(
            datos=datos_solicitud(curso),
            actor_ip="203.0.113.10",
        )

    contador = LimiteSolicitudPublica.objects.get(accion="crear_solicitud")
    assert contador.intentos == 1


@pytest.mark.django_db
def test_consumir_limite_publico_rechaza_el_intento_que_supera_el_maximo():
    ahora = timezone.now()
    for _ in range(2):
        consumir_limite_publico(
            accion="crear_solicitud",
            clave_cruda="203.0.113.10",
            max_intentos=2,
            ventana=timedelta(minutes=10),
            ahora=ahora,
        )

    with pytest.raises(LimiteSolicitudExcedido):
        consumir_limite_publico(
            accion="crear_solicitud",
            clave_cruda="203.0.113.10",
            max_intentos=2,
            ventana=timedelta(minutes=10),
            ahora=ahora,
        )

    contador = LimiteSolicitudPublica.objects.get()
    assert contador.intentos == 2


@pytest.mark.django_db
def test_consumir_limite_publico_elimina_ventanas_vencidas_de_la_misma_accion():
    ahora = timezone.now()
    contador_vencido = LimiteSolicitudPublica.objects.create(
        accion="crear_solicitud",
        clave_hash="a" * 64,
        ventana_inicio=ahora - timedelta(minutes=20),
        intentos=1,
    )
    contador_de_otra_accion = LimiteSolicitudPublica.objects.create(
        accion="corregir_solicitud",
        clave_hash="b" * 64,
        ventana_inicio=ahora - timedelta(hours=2),
        intentos=1,
    )

    consumir_limite_publico(
        accion="crear_solicitud",
        clave_cruda="203.0.113.10",
        max_intentos=30,
        ventana=timedelta(minutes=10),
        ahora=ahora,
    )

    assert not LimiteSolicitudPublica.objects.filter(pk=contador_vencido.pk).exists()
    assert LimiteSolicitudPublica.objects.filter(pk=contador_de_otra_accion.pk).exists()


@pytest.mark.django_db
def test_observar_exige_explicacion_y_rota_el_enlace(curso, actor):
    solicitud = crear_solicitud_directa(curso)
    hash_anterior = solicitud.token_seguimiento_hash

    with pytest.raises(ValueError, match="explicación"):
        observar_solicitud_asociacion(
            solicitud_id=solicitud.pk,
            explicacion="",
            actor=actor,
        )
    resultado = observar_solicitud_asociacion(
        solicitud_id=solicitud.pk,
        explicacion="Corregí el domicilio.",
        actor=actor,
    )

    solicitud.refresh_from_db()
    assert solicitud.estado == SolicitudAsociacion.ESTADO_OBSERVADA
    assert solicitud.token_seguimiento_hash != hash_anterior
    assert resultado.token_seguimiento
    evento = EventoAuditoria.objects.filter(objeto_id=str(solicitud.pk)).latest("id")
    assert evento.motivo == "Corregí el domicilio."
    assert evento.actor == actor


@pytest.mark.django_db
def test_observar_conserva_una_explicacion_de_hasta_500_caracteres(curso, actor):
    solicitud = crear_solicitud_directa(curso)
    explicacion = "x" * 500

    observar_solicitud_asociacion(
        solicitud_id=solicitud.pk,
        explicacion=explicacion,
        actor=actor,
    )

    evento = EventoAuditoria.objects.get(objeto_id=str(solicitud.pk))
    assert evento.motivo == explicacion


@pytest.mark.django_db
def test_corregir_solicitud_cuenta_intento_aunque_el_documento_este_ocupado(
    curso,
):
    solicitud = crear_solicitud_directa(
        curso,
        estado=SolicitudAsociacion.ESTADO_OBSERVADA,
    )
    token = rotar_token_seguimiento(solicitud)
    Asociado.objects.create(
        nombre="Otra",
        apellido="Persona",
        dni="40111222",
        tipo=Asociado.TIPO_ASOCIADO,
        curso_actual=curso,
        fecha_alta=timezone.localdate(),
        fecha_inicio_cobro=timezone.localdate().replace(day=1),
    )

    with pytest.raises(SolicitudAsociacionDuplicada):
        corregir_solicitud_asociacion(
            solicitud_id=solicitud.pk,
            datos=datos_solicitud(curso, dni="40.111.222"),
            token=token,
            actor_ip="203.0.113.10",
        )

    contador = LimiteSolicitudPublica.objects.get(accion="corregir_solicitud")
    assert contador.intentos == 1


@pytest.mark.django_db
def test_aprobar_y_cancelar_respetan_la_maquina_de_estados(curso, actor):
    solicitud = crear_solicitud_directa(curso)

    aprobar_datos_solicitud_asociacion(solicitud_id=solicitud.pk, actor=actor)
    solicitud.refresh_from_db()
    assert solicitud.estado == SolicitudAsociacion.ESTADO_DATOS_APROBADOS

    cancelar_solicitud_asociacion(
        solicitud_id=solicitud.pk,
        motivo="La persona desistió.",
        actor=actor,
    )
    solicitud.refresh_from_db()
    assert solicitud.estado == SolicitudAsociacion.ESTADO_CANCELADA
    assert solicitud.finalizado_en is not None

    with pytest.raises(TransicionSolicitudInvalida):
        aprobar_datos_solicitud_asociacion(
            solicitud_id=solicitud.pk,
            actor=actor,
        )


@pytest.mark.django_db
def test_completar_alta_crea_asociado_cuotas_y_vinculo_una_sola_vez(curso, actor):
    solicitud = crear_solicitud_directa(
        curso,
        estado=SolicitudAsociacion.ESTADO_DATOS_APROBADOS,
    )
    hoy = timezone.localdate()
    ciclo = CicloLectivo.objects.create(anio=hoy.year)
    PeriodoCuota.objects.create(
        ciclo_lectivo=ciclo,
        mes=hoy.month,
        importe=Decimal("1000.00"),
        fecha_vencimiento=hoy.replace(day=10),
    )

    resultado = completar_alta_solicitud_asociacion(
        solicitud_id=solicitud.pk,
        actor=actor,
    )

    solicitud.refresh_from_db()
    assert solicitud.estado == SolicitudAsociacion.ESTADO_ALTA_COMPLETADA
    assert solicitud.asociado == resultado.asociado
    assert resultado.solicitud.pk == solicitud.pk
    assert len(resultado.cuotas_generadas) == 1
    assert Cuota.objects.filter(asociado=resultado.asociado).count() == 1
    with pytest.raises(TransicionSolicitudInvalida):
        completar_alta_solicitud_asociacion(
            solicitud_id=solicitud.pk,
            actor=actor,
        )
    assert Asociado.objects.filter(dni="48123456").count() == 1


@pytest.mark.django_db
def test_completar_alta_revierte_asociado_si_fallan_las_cuotas(
    curso,
    actor,
    monkeypatch,
):
    solicitud = crear_solicitud_directa(
        curso,
        estado=SolicitudAsociacion.ESTADO_DATOS_APROBADOS,
    )
    monkeypatch.setattr(
        "asociados.services.generar_cuotas_iniciales_para_asociado",
        lambda **kwargs: (_ for _ in ()).throw(RuntimeError("falló cuotas")),
    )

    with pytest.raises(RuntimeError, match="falló cuotas"):
        completar_alta_solicitud_asociacion(
            solicitud_id=solicitud.pk,
            actor=actor,
        )

    solicitud.refresh_from_db()
    assert solicitud.estado == SolicitudAsociacion.ESTADO_DATOS_APROBADOS
    assert solicitud.asociado is None
    assert Asociado.objects.count() == 0
