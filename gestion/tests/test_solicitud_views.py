from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.urls import reverse
from django.utils import timezone

from asociados.models import Curso, SolicitudAsociacion
from comunicaciones.models import Comunicacion


@pytest.fixture
def curso():
    return Curso.objects.create(
        anio="1ro",
        curso="1ra",
        division=Curso.DIVISION_CB,
        turno=Curso.TURNO_TM,
    )


def crear_solicitud(curso, *, dni, estado):
    return SolicitudAsociacion.objects.create(
        nombre="Ana",
        apellido="Flores",
        dni=dni,
        email="ana@example.com",
        telefono="2995550192",
        direccion="Los Maitenes 142",
        es_estudiante_cet3=True,
        curso_actual=curso,
        estado=estado,
        token_seguimiento_hash=(dni[-1] * 64),
        token_seguimiento_vence_en=timezone.now() + timedelta(days=30),
    )


def usuario_con_permisos(*codenames):
    usuario = get_user_model().objects.create_user(
        username=f"operador-{get_user_model().objects.count() + 1}",
        password="secreto123",
    )
    usuario.user_permissions.add(
        *Permission.objects.filter(
            content_type__app_label="gestion",
            codename__in=codenames,
        )
    )
    return usuario


@pytest.mark.django_db
def test_bandeja_sin_filtros_muestra_abiertas_y_excluye_finales(client, curso):
    recibida = crear_solicitud(
        curso,
        dni="48111111",
        estado=SolicitudAsociacion.ESTADO_RECIBIDA,
    )
    cancelada = crear_solicitud(
        curso,
        dni="48222222",
        estado=SolicitudAsociacion.ESTADO_CANCELADA,
    )
    usuario = usuario_con_permisos("consultar_solicitudes_asociacion")
    client.force_login(usuario)

    response = client.get(reverse("gestion:solicitudes_asociacion"))

    assert response.status_code == 200
    assert recibida in response.context["solicitudes"]
    assert cancelada not in response.context["solicitudes"]
    contenido = response.content.decode()
    assert "Todas las solicitudes abiertas" in contenido
    assert 'class="bi bi-funnel"' in contenido
    assert "Limpiar filtros" not in contenido
    assert "uni2-records-table" in contenido
    assert "uni2-clickable-row" in contenido
    assert 'class="uni2-row-link' in contenido
    assert 'data-label="Documento"' in contenido
    assert 'data-label="Estado"' in contenido
    assert "uni2-avatar" in contenido
    assert "1 solicitud encontrada" in contenido


@pytest.mark.django_db
def test_bandeja_permite_filtrar_un_estado_final(client, curso):
    recibida = crear_solicitud(
        curso,
        dni="48111111",
        estado=SolicitudAsociacion.ESTADO_RECIBIDA,
    )
    cancelada = crear_solicitud(
        curso,
        dni="48222222",
        estado=SolicitudAsociacion.ESTADO_CANCELADA,
    )
    usuario = usuario_con_permisos("consultar_solicitudes_asociacion")
    client.force_login(usuario)

    response = client.get(
        reverse("gestion:solicitudes_asociacion"),
        {"estado": SolicitudAsociacion.ESTADO_CANCELADA},
    )

    assert cancelada in response.context["solicitudes"]
    assert recibida not in response.context["solicitudes"]
    contenido = response.content.decode()
    assert 'class="bi bi-x-circle"' in contenido
    assert "Limpiar filtros" in contenido
    assert "uni2-badge-danger" in contenido


@pytest.mark.django_db
def test_bandeja_permite_ver_todas_las_solicitudes(client, curso):
    recibida = crear_solicitud(
        curso,
        dni="48111111",
        estado=SolicitudAsociacion.ESTADO_RECIBIDA,
    )
    cancelada = crear_solicitud(
        curso,
        dni="48222222",
        estado=SolicitudAsociacion.ESTADO_CANCELADA,
    )
    usuario = usuario_con_permisos("consultar_solicitudes_asociacion")
    client.force_login(usuario)

    response = client.get(
        reverse("gestion:solicitudes_asociacion"),
        {"estado": "todas"},
    )

    assert recibida in response.context["solicitudes"]
    assert cancelada in response.context["solicitudes"]
    assert "Todas las solicitudes" in response.content.decode()


@pytest.mark.django_db
def test_bandeja_requiere_permiso_de_consulta(client):
    usuario = get_user_model().objects.create_user(
        username="sin-permiso",
        password="secreto123",
    )
    client.force_login(usuario)

    response = client.get(reverse("gestion:solicitudes_asociacion"))

    assert response.status_code == 403


@pytest.mark.django_db
def test_detalle_muestra_datos_y_oculta_acciones_sin_permiso(client, curso):
    solicitud = crear_solicitud(
        curso,
        dni="48111111",
        estado=SolicitudAsociacion.ESTADO_RECIBIDA,
    )
    usuario = usuario_con_permisos("consultar_solicitudes_asociacion")
    client.force_login(usuario)

    response = client.get(
        reverse("gestion:solicitud_asociacion_detalle", args=[solicitud.pk])
    )
    contenido = response.content.decode()

    assert response.status_code == 200
    assert "Flores, Ana" in contenido
    assert "48111111" in contenido
    assert "Aprobar datos" not in contenido
    assert "Cancelar solicitud" not in contenido


@pytest.mark.django_db
def test_observar_exige_explicacion_y_programa_correo(client, curso):
    solicitud = crear_solicitud(
        curso,
        dni="48111111",
        estado=SolicitudAsociacion.ESTADO_RECIBIDA,
    )
    usuario = usuario_con_permisos(
        "consultar_solicitudes_asociacion",
        "revisar_solicitudes_asociacion",
    )
    client.force_login(usuario)
    url = reverse("gestion:solicitud_asociacion_observar", args=[solicitud.pk])

    formulario = client.get(url).content.decode()
    assert 'name="explicacion"' in formulario
    assert "autofocus" in formulario
    assert ">Solicitudes de asociación</a>" in formulario
    assert ">Flores, Ana</a>" in formulario
    assert 'aria-current="page">Observar solicitud</li>' in formulario
    assert "uni2-section-kicker" not in formulario

    invalida = client.post(url, {"explicacion": ""})
    valida = client.post(url, {"explicacion": "Corregí el domicilio."})

    solicitud.refresh_from_db()
    assert invalida.status_code == 200
    assert valida.status_code == 302
    assert solicitud.estado == SolicitudAsociacion.ESTADO_OBSERVADA
    assert Comunicacion.objects.get().tipo == "preinscripcion_observada"
    detalle = client.get(
        reverse("gestion:solicitud_asociacion_detalle", args=[solicitud.pk])
    ).content.decode()
    assert "Solicitud observada" in detalle
    assert "Corregí el domicilio." in detalle


@pytest.mark.django_db
def test_aprobar_datos_es_post_y_programa_correo(client, curso):
    solicitud = crear_solicitud(
        curso,
        dni="48111111",
        estado=SolicitudAsociacion.ESTADO_RECIBIDA,
    )
    usuario = usuario_con_permisos(
        "consultar_solicitudes_asociacion",
        "revisar_solicitudes_asociacion",
    )
    client.force_login(usuario)
    url = reverse("gestion:solicitud_asociacion_aprobar", args=[solicitud.pk])

    detalle_recibida = client.get(
        reverse("gestion:solicitud_asociacion_detalle", args=[solicitud.pk])
    ).content.decode()
    assert "Aprobar datos" in detalle_recibida
    assert "Aprobar documentación" not in detalle_recibida

    assert client.get(url).status_code == 405
    response = client.post(url)

    solicitud.refresh_from_db()
    assert response.status_code == 302
    assert solicitud.estado == SolicitudAsociacion.ESTADO_DATOS_APROBADOS
    assert Comunicacion.objects.get().tipo == "preinscripcion_datos_aprobados"

    detalle = client.get(
        reverse("gestion:solicitud_asociacion_detalle", args=[solicitud.pk])
    ).content.decode()
    assert "uni2-badge-success" in detalle
    assert "Datos aprobados" in detalle
    assert "Los datos quedaron aprobados." in detalle
    assert "preinscripcion_datos_aprobados" not in detalle
    assert "bi-eye" in detalle
    assert "bi-envelope" in detalle
    assert "Cambios relacionados" not in detalle
    assert 'class="uni2-timeline"' in detalle
    assert 'class="uni2-timeline-item"' in detalle
    assert 'class="uni2-timeline-marker"' in detalle


@pytest.mark.django_db
def test_cancelar_exige_motivo_y_cierra_definitivamente(client, curso):
    solicitud = crear_solicitud(
        curso,
        dni="48111111",
        estado=SolicitudAsociacion.ESTADO_RECIBIDA,
    )
    usuario = usuario_con_permisos(
        "consultar_solicitudes_asociacion",
        "cancelar_solicitudes_asociacion",
    )
    client.force_login(usuario)
    url = reverse("gestion:solicitud_asociacion_cancelar", args=[solicitud.pk])

    assert client.post(url, {"motivo": ""}).status_code == 200
    response = client.post(url, {"motivo": "La persona desistió."})

    solicitud.refresh_from_db()
    assert response.status_code == 302
    assert solicitud.estado == SolicitudAsociacion.ESTADO_CANCELADA
    assert Comunicacion.objects.get().tipo == "preinscripcion_cancelada"
    detalle = client.get(
        reverse("gestion:solicitud_asociacion_detalle", args=[solicitud.pk])
    ).content.decode()
    assert "Solicitud cancelada" in detalle
    assert "La persona desistió." in detalle


@pytest.mark.django_db
def test_completar_alta_crea_usuario_y_programa_correo(client, curso):
    solicitud = crear_solicitud(
        curso,
        dni="48111111",
        estado=SolicitudAsociacion.ESTADO_DATOS_APROBADOS,
    )
    usuario = usuario_con_permisos(
        "consultar_solicitudes_asociacion",
        "revisar_solicitudes_asociacion",
        "completar_solicitudes_asociacion",
        "cancelar_solicitudes_asociacion",
        "reenviar_comunicaciones",
    )
    client.force_login(usuario)

    detalle = client.get(
        reverse("gestion:solicitud_asociacion_detalle", args=[solicitud.pk])
    ).content.decode()
    assert "bi-person-check" in detalle
    assert "bi-eye" in detalle
    assert "bi-x-circle" in detalle
    assert "Reenviar correo del estado actual" in detalle

    confirmacion = client.get(
        reverse("gestion:solicitud_asociacion_completar", args=[solicitud.pk])
    ).content.decode()
    assert "Confirmar alta" in confirmacion
    assert "Flores, Ana" in confirmacion
    assert "48111111" in confirmacion
    assert "1ro 1ra CB TM" in confirmacion
    assert "Se creará el asociado" in confirmacion
    assert "Se generarán sus cuotas iniciales" in confirmacion
    assert "No registra ningún pago" in confirmacion
    assert "Confirmar y crear asociado" in confirmacion
    assert "bi-person-check" in confirmacion
    assert "bi-arrow-left" in confirmacion
    assert "Volver</a>" in confirmacion

    response = client.post(
        reverse("gestion:solicitud_asociacion_completar", args=[solicitud.pk]),
        {"confirmar": "si"},
    )

    solicitud.refresh_from_db()
    assert response.status_code == 302
    assert response.url == reverse(
        "gestion:asociado_detalle",
        args=[solicitud.asociado_id],
    )
    assert solicitud.estado == SolicitudAsociacion.ESTADO_ALTA_COMPLETADA
    assert solicitud.asociado.usuario_id is not None
    assert Comunicacion.objects.filter(
        tipo="alta_usuario",
        origen_entidad="asociados.Asociado",
        origen_id=str(solicitud.asociado_id),
    ).count() == 1

    detalle_solicitud = client.get(
        reverse("gestion:solicitud_asociacion_detalle", args=[solicitud.pk])
    ).content.decode()
    asociado_url = reverse("gestion:asociado_detalle", args=[solicitud.asociado_id])
    assert asociado_url in detalle_solicitud
    assert "Ver asociado" in detalle_solicitud
    assert "bi-person-vcard" in detalle_solicitud
    assert f"N.º {solicitud.asociado.numero_asociado}" in detalle_solicitud


@pytest.mark.django_db
def test_reenviar_comunicacion_rota_enlace_y_crea_nueva_entrega(client, curso):
    solicitud = crear_solicitud(
        curso,
        dni="48111111",
        estado=SolicitudAsociacion.ESTADO_RECIBIDA,
    )
    hash_anterior = solicitud.token_seguimiento_hash
    usuario = usuario_con_permisos(
        "consultar_solicitudes_asociacion",
        "reenviar_comunicaciones",
    )
    client.force_login(usuario)

    response = client.post(
        reverse("gestion:solicitud_asociacion_reenviar", args=[solicitud.pk])
    )

    solicitud.refresh_from_db()
    assert response.status_code == 302
    assert solicitud.token_seguimiento_hash != hash_anterior
    assert Comunicacion.objects.count() == 1
