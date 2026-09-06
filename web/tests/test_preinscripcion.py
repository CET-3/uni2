import re
import uuid

import pytest
from django.test import override_settings
from django.urls import reverse

from asociados.models import Asociado, ClasificacionAdherente, Curso, SolicitudAsociacion
from asociados.selectors import obtener_solicitud_por_token
from asociados.services import rotar_token_seguimiento
from auditoria.models import EventoAuditoria
from comunicaciones.models import Comunicacion, EntregaComunicacion
from web.forms import SolicitudAsociacionForm


@pytest.fixture
def curso():
    return Curso.objects.create(
        anio="1ro",
        curso="1ra",
        division=Curso.DIVISION_CB,
        turno=Curso.TURNO_TM,
    )


def datos_formulario(**overrides):
    datos = {
        "clave_operacion": str(uuid.uuid4()),
        "nombre": "Ana",
        "apellido": "Flores",
        "dni": "48.123.456",
        "email": "ana@example.com",
        "telefono": "2995550192",
        "direccion": "Los Maitenes 142",
        "es_estudiante_cet3": "si",
        "curso_actual": "",
        "clasificacion_adherente": "",
    }
    datos.update(overrides)
    return datos


@pytest.mark.django_db
def test_reintento_misma_preinscripcion_confirma_sin_duplicar(client, curso):
    datos = datos_formulario(curso_actual=str(curso.pk))
    primera = client.post(reverse("web:preinscripcion"), datos)
    eventos = EventoAuditoria.objects.count()
    comunicaciones = Comunicacion.objects.count()
    entregas = EntregaComunicacion.objects.count()
    segunda = client.post(reverse("web:preinscripcion"), datos)
    assert primera.status_code == segunda.status_code == 302
    assert primera.url == segunda.url == reverse("web:preinscripcion_recibida")
    assert SolicitudAsociacion.objects.count() == 1
    assert EventoAuditoria.objects.count() == eventos
    assert Comunicacion.objects.count() == comunicaciones == 1
    assert EntregaComunicacion.objects.count() == entregas == 1
    distinta = client.post(reverse("web:preinscripcion"), {**datos, "clave_operacion": str(uuid.uuid4())})
    assert distinta.status_code == 200
    assert "otra solicitud" in distinta.content.decode()


@pytest.mark.django_db
@pytest.mark.parametrize("clave", ["", "no-es-un-uuid"])
def test_preinscripcion_exige_clave_valida(client, curso, clave):
    response = client.post(reverse("web:preinscripcion"), datos_formulario(curso_actual=curso.pk, clave_operacion=clave))
    assert response.status_code == 200
    assert "Recargá la página" in response.content.decode()
    assert not SolicitudAsociacion.objects.exists()


def solicitud_con_token(curso, *, estado=SolicitudAsociacion.ESTADO_RECIBIDA):
    solicitud = SolicitudAsociacion.objects.create(
        nombre="Ana",
        apellido="Flores",
        dni="48123456",
        email="ana@example.com",
        telefono="2995550192",
        direccion="Los Maitenes 142",
        es_estudiante_cet3=True,
        curso_actual=curso,
        estado=estado,
        token_seguimiento_hash="a" * 64,
        token_seguimiento_vence_en="2026-09-25T12:00:00-03:00",
    )
    return solicitud, rotar_token_seguimiento(solicitud)


@pytest.mark.django_db
def test_formulario_marca_campos_invalidos_con_descripcion_accesible():
    form = SolicitudAsociacionForm(data={})

    assert not form.is_valid()
    assert form.fields["nombre"].widget.attrs["class"] == "form-control is-invalid"
    assert form.fields["nombre"].widget.attrs["aria-invalid"] == "true"
    assert form.fields["nombre"].widget.attrs["aria-describedby"] == "id_nombre-errors"
    assert "autofocus" not in form.fields["nombre"].widget.attrs
    assert "is-invalid" not in form.fields["es_estudiante_cet3"].widget.attrs["class"]


@pytest.mark.django_db
def test_formulario_nuevo_enfoca_el_primer_campo():
    form = SolicitudAsociacionForm()

    assert form.fields["nombre"].widget.attrs["autofocus"] is True


@pytest.mark.django_db
def test_formulario_publico_presenta_errores_e_iconos_del_design_system(client):
    response = client.post(reverse("web:preinscripcion"), {})
    contenido = response.content.decode()

    assert response.status_code == 200
    assert "uni2-field-error" in contenido
    assert "bi-exclamation-circle-fill" in contenido
    assert re.search(r'<button[^>]*>\s*<i class="bi bi-send"', contenido)
    assert re.search(r'<a[^>]*>\s*<i class="bi bi-arrow-left"', contenido)
    assert "uni2-preinscription-form" in contenido
    assert 'class="card-body p-3 p-md-4"' in contenido
    assert 'class="uni2-form-error-focus" tabindex="-1" autofocus' in contenido
    assert "errorlist" not in contenido
    assert "Unite a la Mutual" not in contenido
    assert "uni2-breadcrumbs" not in contenido
    assert "<title>Preinscripción | Uni2</title>" in contenido


@pytest.mark.django_db
def test_formulario_publico_deriva_asociado_y_redirige(client, curso):
    response = client.post(
        reverse("web:preinscripcion"),
        datos_formulario(curso_actual=curso.pk),
    )

    assert response.status_code == 302
    assert response.url == reverse("web:preinscripcion_recibida")
    solicitud = SolicitudAsociacion.objects.get()
    assert solicitud.tipo == Asociado.TIPO_ASOCIADO
    assert solicitud.curso_actual == curso
    assert solicitud.clasificacion_adherente is None


@pytest.mark.django_db
def test_formulario_publico_deriva_adherente_y_redirige(client):
    clasificacion = ClasificacionAdherente.objects.get(nombre="Familiar")

    response = client.post(
        reverse("web:preinscripcion"),
        datos_formulario(
            dni="BO-12345-A",
            es_estudiante_cet3="no",
            clasificacion_adherente=clasificacion.pk,
        ),
    )

    assert response.status_code == 302
    solicitud = SolicitudAsociacion.objects.get()
    assert solicitud.tipo == Asociado.TIPO_ADHERENTE
    assert solicitud.clasificacion_adherente == clasificacion
    assert solicitud.curso_actual is None


@pytest.mark.django_db
def test_formulario_exige_curso_o_clasificacion_segun_respuesta(client, curso):
    sin_curso = client.post(
        reverse("web:preinscripcion"),
        datos_formulario(),
    )
    sin_clasificacion = client.post(
        reverse("web:preinscripcion"),
        datos_formulario(
            dni="BO-12345-A",
            es_estudiante_cet3="no",
        ),
    )

    assert sin_curso.status_code == 200
    assert "Elegí tu curso" in sin_curso.content.decode()
    assert sin_clasificacion.status_code == 200
    assert "Elegí una categoría" in sin_clasificacion.content.decode()
    assert SolicitudAsociacion.objects.count() == 0


@pytest.mark.django_db
def test_formulario_no_expone_si_el_documento_ya_esta_registrado(client, curso):
    Asociado.objects.create(
        nombre="Ana",
        apellido="Flores",
        dni="48123456",
        tipo=Asociado.TIPO_ASOCIADO,
        curso_actual=curso,
        fecha_alta="2026-08-01",
        fecha_inicio_cobro="2026-06-01",
    )

    response = client.post(
        reverse("web:preinscripcion"),
        datos_formulario(curso_actual=curso.pk),
    )
    contenido = response.content.decode()

    assert response.status_code == 200
    assert "Es posible que el documento ya esté asociado" in contenido
    assert "contactate con la Mutual" in contenido
    assert "Revisá los datos del formulario" not in contenido
    assert contenido.count("uni2-alert-danger") == 1
    assert contenido.count("autofocus") == 1
    assert 'class="uni2-form-error-focus" tabindex="-1" autofocus' in contenido
    assert "is-invalid" not in contenido
    assert "ya existe" not in contenido.lower()
    assert SolicitudAsociacion.objects.count() == 0


@pytest.mark.django_db
@override_settings(UNI2_SOLICITUD_CREACION_MAX_INTENTOS=0)
def test_formulario_distingue_el_exceso_de_intentos_de_un_documento_existente(
    client, curso
):
    response = client.post(
        reverse("web:preinscripcion"),
        datos_formulario(curso_actual=curso.pk),
    )
    contenido = response.content.decode()

    assert response.status_code == 200
    assert "Realizaste varios intentos" in contenido
    assert "Esperá unos minutos" in contenido
    assert "Es posible que el documento ya esté asociado" not in contenido
    assert contenido.count("uni2-alert-danger") == 1
    assert "is-invalid" not in contenido
    assert SolicitudAsociacion.objects.count() == 0


@pytest.mark.django_db
def test_preinscripcion_y_confirmacion_no_son_cacheables(client):
    for url_name in ("web:preinscripcion", "web:preinscripcion_recibida"):
        response = client.get(reverse(url_name))

        assert response.status_code == 200
        assert "no-store" in response.headers["Cache-Control"]
        assert response.headers["X-Robots-Tag"] == "noindex, nofollow"
        assert "X-Uni2-PWA-Cacheable" not in response.headers


@pytest.mark.django_db
def test_confirmacion_no_muestra_datos_personales(client):
    response = client.get(reverse("web:preinscripcion_recibida"))
    contenido = response.content.decode()

    assert "Recibimos tu preinscripción" in contenido
    assert "uni2-preinscription-result" in contenido
    assert "En revisión" in contenido
    assert "bi-house" in contenido
    assert "d-grid d-sm-block" in contenido
    assert "correo no deseado" in contenido
    assert "DNI" not in contenido
    assert "correo enviado a" not in contenido.lower()


@pytest.mark.django_db
def test_confirmacion_de_correcciones_usa_resultado_unificado(client):
    response = client.get(reverse("web:preinscripcion_correcciones_recibidas"))
    contenido = response.content.decode()

    assert response.status_code == 200
    assert "uni2-preinscription-result" in contenido
    assert "Recibimos tus correcciones" in contenido
    assert "En revisión" in contenido
    assert "nuevo enlace privado de seguimiento" in contenido
    assert "correo no deseado" in contenido
    assert "bi-house" in contenido


@pytest.mark.django_db
def test_seguimiento_recibido_muestra_estado_pero_no_formulario(client, curso):
    _, token = solicitud_con_token(curso)

    response = client.get(reverse("web:solicitud_seguimiento", args=[token]))
    contenido = response.content.decode()

    assert response.status_code == 200
    assert "Recibida" in contenido
    assert "Enviar correcciones" not in contenido
    assert "48123456" not in contenido


@pytest.mark.django_db
def test_seguimiento_datos_aprobados_muestra_estado_sin_documentacion(client, curso):
    _, token = solicitud_con_token(
        curso,
        estado=SolicitudAsociacion.ESTADO_DATOS_APROBADOS,
    )

    response = client.get(reverse("web:solicitud_seguimiento", args=[token]))
    contenido = response.content.decode()

    assert response.status_code == 200
    assert "Datos aprobados" in contenido
    assert "Documentación aprobada" not in contenido


@pytest.mark.django_db
def test_seguimiento_observado_muestra_explicacion_y_formulario(client, curso):
    solicitud, token = solicitud_con_token(
        curso,
        estado=SolicitudAsociacion.ESTADO_OBSERVADA,
    )
    EventoAuditoria.objects.create(
        actor_etiqueta="María Operadora",
        accion=EventoAuditoria.ACCION_CAMBIAR_ESTADO,
        entidad=solicitud._meta.label,
        objeto_id=str(solicitud.pk),
        objeto_descripcion=str(solicitud),
        cambios={
            "estado": {
                "anterior": SolicitudAsociacion.ESTADO_RECIBIDA,
                "nuevo": SolicitudAsociacion.ESTADO_OBSERVADA,
            }
        },
        motivo="Corregí el domicilio.",
        origen=EventoAuditoria.ORIGEN_GESTION,
    )

    response = client.get(reverse("web:solicitud_seguimiento", args=[token]))
    contenido = response.content.decode()

    assert "Corregí el domicilio." in contenido
    assert "Enviar correcciones" in contenido
    assert 'value="Ana"' in contenido
    assert re.search(r'<input[^>]+name="nombre"[^>]+autofocus', contenido)


@pytest.mark.django_db
def test_seguimiento_observado_reutiliza_presentacion_de_errores(client, curso):
    _, token = solicitud_con_token(
        curso,
        estado=SolicitudAsociacion.ESTADO_OBSERVADA,
    )

    response = client.post(reverse("web:solicitud_seguimiento", args=[token]), {})
    contenido = response.content.decode()

    assert response.status_code == 200
    assert "uni2-field-error" in contenido
    assert "bi-exclamation-circle-fill" in contenido
    assert "errorlist" not in contenido
    assert 'class="uni2-form-error-focus" tabindex="-1" autofocus' in contenido


@pytest.mark.django_db
def test_corregir_solicitud_invalida_token_anterior_y_vuelve_a_recibida(client, curso):
    solicitud, token = solicitud_con_token(
        curso,
        estado=SolicitudAsociacion.ESTADO_OBSERVADA,
    )

    response = client.post(
        reverse("web:solicitud_seguimiento", args=[token]),
        datos_formulario(
            apellido="Flores Corregido",
            curso_actual=curso.pk,
        ),
    )

    solicitud.refresh_from_db()
    assert response.status_code == 302
    assert response.url == reverse("web:preinscripcion_correcciones_recibidas")
    assert solicitud.estado == SolicitudAsociacion.ESTADO_RECIBIDA
    assert solicitud.apellido == "Flores Corregido"
    assert obtener_solicitud_por_token(token) is None


@pytest.mark.django_db
def test_token_invalido_no_revela_existencia(client):
    response = client.get(
        reverse("web:solicitud_seguimiento", args=["token-invalido"])
    )
    contenido = response.content.decode()

    assert response.status_code == 200
    assert "El enlace no está disponible" in contenido
    assert "DNI" not in contenido
    assert response.headers["X-Robots-Tag"] == "noindex, nofollow"
