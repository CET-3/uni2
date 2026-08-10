import uuid

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.urls import reverse

from asociados.models import Asociado, CicloLectivo
from auditoria.models import EventoAuditoria
from cuotas.models import PeriodoCuota
from gestion.permissions import (
    GESTION_ADMINISTRAR_PERIODOS_CUOTA,
    GESTION_CONSULTAR_ASOCIADOS,
    GESTION_DASHBOARD,
    GESTION_EDITAR_ASOCIADOS,
    GESTION_VER_AUDITORIA,
)


def crear_usuario_con_permisos(username, permisos):
    usuario = get_user_model().objects.create_user(username=username, password="secreto123")
    codenames = [permiso.split(".", 1)[1] for permiso in permisos]
    usuario.user_permissions.add(
        *Permission.objects.filter(content_type__app_label="gestion", codename__in=codenames)
    )
    return usuario


@pytest.mark.django_db
def test_auditoria_rechaza_usuario_sin_permiso_y_oculta_acceso(client):
    usuario = crear_usuario_con_permisos("sin_auditoria", [GESTION_DASHBOARD])
    client.force_login(usuario)

    dashboard = client.get(reverse("web:home"))
    auditoria = client.get(reverse("gestion:auditoria"))

    assert dashboard.status_code == 200
    assert reverse("gestion:auditoria") not in dashboard.content.decode()
    assert auditoria.status_code == 403


@pytest.mark.django_db
def test_auditoria_muestra_acceso_y_eventos_con_permiso(client):
    usuario = crear_usuario_con_permisos("con_auditoria", [GESTION_DASHBOARD, GESTION_VER_AUDITORIA])
    EventoAuditoria.objects.create(
        actor=usuario,
        actor_etiqueta=usuario.username,
        accion=EventoAuditoria.ACCION_MODIFICAR,
        entidad="asociados.Asociado",
        objeto_id="7",
        objeto_descripcion="Campos, Julia",
        cambios={"telefono": {"anterior": "123", "nuevo": "456"}},
        origen=EventoAuditoria.ORIGEN_GESTION,
    )
    client.force_login(usuario)

    dashboard = client.get(reverse("web:home"))
    auditoria = client.get(reverse("gestion:auditoria"))

    assert reverse("gestion:auditoria") in dashboard.content.decode()
    assert auditoria.status_code == 200
    contenido = auditoria.content.decode()
    assert "Campos, Julia" in contenido
    assert "con_auditoria" in contenido
    assert "Teléfono" in contenido
    assert "modificó" in contenido
    assert "el día" in contenido
    assert "Entidad:" in contenido
    assert "Asociado" in contenido
    assert "<details" not in contenido
    assert "uni2-audit-event" in contenido


@pytest.mark.django_db
def test_filtros_de_auditoria_muestran_busqueda_clara_y_entidades_disponibles(client):
    usuario = crear_usuario_con_permisos("auditora_filtros", [GESTION_VER_AUDITORIA])
    EventoAuditoria.objects.create(
        actor=usuario,
        actor_etiqueta=usuario.username,
        accion=EventoAuditoria.ACCION_MODIFICAR,
        entidad="asociados.Asociado",
        objeto_id="70",
        objeto_descripcion="Campos, Julia",
        cambios={},
        origen=EventoAuditoria.ORIGEN_GESTION,
    )
    client.force_login(usuario)

    response = client.get(
        reverse("gestion:auditoria"),
        {"entidad": "asociados.Asociado"},
    )
    contenido = response.content.decode()

    assert "Persona que realizó la acción" in contenido
    assert 'placeholder="Nombre, apellido o usuario"' in contenido
    assert "Objeto modificado" in contenido
    assert 'placeholder="Nombre, descripción o ID"' in contenido
    assert '<select name="entidad"' in contenido
    assert '<option value="">Todas las entidades</option>' in contenido
    assert '<option value="asociados.Asociado" selected>Asociado</option>' in contenido


@pytest.mark.django_db
def test_alta_y_edicion_desde_gestion_generan_eventos(client):
    usuario = crear_usuario_con_permisos(
        "operadora",
        [GESTION_CONSULTAR_ASOCIADOS, GESTION_EDITAR_ASOCIADOS, GESTION_VER_AUDITORIA],
    )
    client.force_login(usuario)

    client.post(
        reverse("gestion:asociado_nuevo"),
        {
            "nombre": "Mara",
            "apellido": "López",
            "dni": "44111229",
            "email": "mara@example.com",
            "telefono": "111",
            "direccion": "Calle 1",
            "tipo": Asociado.TIPO_ASOCIADO,
            "curso_actual": "",
            "fecha_alta": "2026-08-09",
        },
    )
    asociado = Asociado.objects.get(dni="44111229")
    evento_alta = EventoAuditoria.objects.get(
        accion=EventoAuditoria.ACCION_CREAR,
        entidad="asociados.Asociado",
        objeto_id=str(asociado.pk),
    )

    client.post(
        reverse("gestion:asociado_editar", args=[asociado.pk]),
        {
            "nombre": "Mara",
            "apellido": "López",
            "dni": "44111229",
            "email": "mara@example.com",
            "telefono": "222",
            "direccion": "Calle 1",
            "tipo": Asociado.TIPO_ASOCIADO,
            "curso_actual": "",
            "estado": Asociado.ESTADO_ACTIVO,
            "fecha_alta": "2026-08-09",
            "fecha_inicio_cobro": "2026-08-01",
            "fecha_baja": "",
            "motivo_baja": "",
        },
    )
    evento_edicion = EventoAuditoria.objects.get(
        accion=EventoAuditoria.ACCION_MODIFICAR,
        entidad="asociados.Asociado",
        objeto_id=str(asociado.pk),
    )

    assert evento_alta.actor == usuario
    assert evento_alta.origen == EventoAuditoria.ORIGEN_GESTION
    assert "token_credencial" not in evento_alta.cambios
    assert evento_edicion.cambios == {"telefono": {"anterior": "111", "nuevo": "222"}}
    eventos_operacion_alta = EventoAuditoria.objects.filter(operacion_id=evento_alta.operacion_id)
    assert set(eventos_operacion_alta.values_list("entidad", "accion")) == {
        ("auth.User", EventoAuditoria.ACCION_CREAR),
        ("asociados.Asociado", EventoAuditoria.ACCION_VINCULAR),
        ("asociados.Asociado", EventoAuditoria.ACCION_CREAR),
    }


@pytest.mark.django_db
def test_auditoria_presenta_relaciones_y_campos_en_formato_legible(client):
    usuario = crear_usuario_con_permisos("auditora_cursos", [GESTION_VER_AUDITORIA])
    EventoAuditoria.objects.create(
        actor=usuario,
        actor_etiqueta=usuario.username,
        accion=EventoAuditoria.ACCION_MODIFICAR,
        entidad="asociados.Asociado",
        objeto_id="8",
        objeto_descripcion="Campos, Julia",
        cambios={
            "curso_actual": {
                "anterior": {"id": 65, "texto": "2do 1ra CB TM"},
                "nuevo": {"id": 71, "texto": "3ro 3ra CS TM"},
            }
        },
        origen=EventoAuditoria.ORIGEN_GESTION,
    )
    client.force_login(usuario)

    response = client.get(reverse("gestion:auditoria"))
    contenido = response.content.decode()

    assert response.status_code == 200
    assert "Curso actual" in contenido
    assert "2do 1ra CB TM" in contenido
    assert "3ro 3ra CS TM" in contenido
    assert "&#x27;id&#x27;" not in contenido


@pytest.mark.django_db
def test_detalle_asociado_no_expone_acceso_contextual_a_auditoria(client):
    con_permiso = crear_usuario_con_permisos(
        "detalle_con_auditoria",
        [GESTION_CONSULTAR_ASOCIADOS, GESTION_VER_AUDITORIA],
    )
    sin_permiso = crear_usuario_con_permisos(
        "detalle_sin_auditoria",
        [GESTION_CONSULTAR_ASOCIADOS],
    )
    asociado = Asociado.objects.create(
        nombre="Julia",
        apellido="Campos",
        dni="40000999",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta="2026-08-09",
        fecha_inicio_cobro="2026-08-01",
    )
    url_detalle = reverse("gestion:asociado_detalle", args=[asociado.pk])
    client.force_login(con_permiso)
    contenido_con_permiso = client.get(url_detalle).content.decode()
    client.force_login(sin_permiso)
    contenido_sin_permiso = client.get(url_detalle).content.decode()

    assert "Ver auditoría" not in contenido_con_permiso
    assert "Ver auditoría" not in contenido_sin_permiso


@pytest.mark.django_db
def test_auditoria_contextual_filtra_por_asociado(client):
    usuario = crear_usuario_con_permisos("auditoria_contextual", [GESTION_VER_AUDITORIA])
    for objeto_id, descripcion in (("10", "Campos, Julia"), ("11", "Rivas, Mora")):
        EventoAuditoria.objects.create(
            actor=usuario,
            actor_etiqueta=usuario.username,
            accion=EventoAuditoria.ACCION_MODIFICAR,
            entidad="asociados.Asociado",
            objeto_id=objeto_id,
            objeto_descripcion=descripcion,
            cambios={},
            origen=EventoAuditoria.ORIGEN_GESTION,
        )
    client.force_login(usuario)

    response = client.get(
        reverse("gestion:auditoria"),
        {"entidad": "asociados.Asociado", "objeto_id": "10"},
    )
    contenido = response.content.decode()

    assert "Campos, Julia" in contenido
    assert "Rivas, Mora" not in contenido


@pytest.mark.django_db
def test_auditoria_agrupa_la_operacion_sin_ocultar_eventos(client):
    usuario = crear_usuario_con_permisos("auditora_operaciones", [GESTION_VER_AUDITORIA])
    operacion_id = uuid.uuid4()
    for objeto_id, descripcion, telefono in (
        ("20", "Campos, Julia", "111"),
        ("21", "Rivas, Mora", "222"),
    ):
        EventoAuditoria.objects.create(
            actor=usuario,
            actor_etiqueta=usuario.username,
            accion=EventoAuditoria.ACCION_MODIFICAR,
            entidad="asociados.Asociado",
            objeto_id=objeto_id,
            objeto_descripcion=descripcion,
            cambios={"telefono": {"anterior": "000", "nuevo": telefono}},
            origen=EventoAuditoria.ORIGEN_GESTION,
            operacion_id=operacion_id,
        )
    client.force_login(usuario)

    response = client.get(reverse("gestion:auditoria"))
    contenido = response.content.decode()

    assert response.status_code == 200
    assert len(response.context["page_obj"].object_list) == 1
    assert "Cambios relacionados" in contenido
    assert "2 eventos relacionados" in contenido
    assert str(operacion_id) in contenido
    assert "Campos, Julia" in contenido
    assert "Rivas, Mora" in contenido
    assert "111" in contenido
    assert "222" in contenido


@pytest.mark.django_db
def test_filtro_de_auditoria_muestra_toda_la_operacion_relacionada(client):
    usuario = crear_usuario_con_permisos("auditora_filtro_operacion", [GESTION_VER_AUDITORIA])
    operacion_id = uuid.uuid4()
    for objeto_id, descripcion in (("30", "Coincide"), ("31", "Evento relacionado")):
        EventoAuditoria.objects.create(
            actor=usuario,
            actor_etiqueta=usuario.username,
            accion=EventoAuditoria.ACCION_MODIFICAR,
            entidad="asociados.Asociado",
            objeto_id=objeto_id,
            objeto_descripcion=descripcion,
            cambios={},
            origen=EventoAuditoria.ORIGEN_GESTION,
            operacion_id=operacion_id,
        )
    client.force_login(usuario)

    response = client.get(reverse("gestion:auditoria"), {"objeto_id": "30"})
    contenido = response.content.decode()

    assert "Coincide" in contenido
    assert "Evento relacionado" in contenido


@pytest.mark.django_db
def test_auditoria_pagina_por_operaciones(client):
    usuario = crear_usuario_con_permisos("auditora_paginacion", [GESTION_VER_AUDITORIA])
    for numero in range(26):
        operacion_id = uuid.uuid4()
        cantidad_eventos = 2 if numero == 25 else 1
        for relacionado in range(cantidad_eventos):
            EventoAuditoria.objects.create(
                actor=usuario,
                actor_etiqueta=usuario.username,
                accion=EventoAuditoria.ACCION_CREAR,
                entidad="asociados.Asociado",
                objeto_id=f"{numero}-{relacionado}",
                objeto_descripcion=f"Operación {numero}",
                cambios={},
                origen=EventoAuditoria.ORIGEN_GESTION,
                operacion_id=operacion_id,
            )
    client.force_login(usuario)

    primera_pagina = client.get(reverse("gestion:auditoria"))
    segunda_pagina = client.get(reverse("gestion:auditoria"), {"page": "2"})

    assert primera_pagina.context["page_obj"].paginator.count == 26
    assert len(primera_pagina.context["page_obj"].object_list) == 25
    assert len(segunda_pagina.context["page_obj"].object_list) == 1


@pytest.mark.django_db
def test_creacion_y_generacion_de_periodo_desde_gestion_identifican_actor(client):
    usuario = crear_usuario_con_permisos(
        "administradora_periodos",
        [GESTION_ADMINISTRAR_PERIODOS_CUOTA],
    )
    ciclo = CicloLectivo.objects.create(anio=2026)
    asociado = Asociado.objects.create(
        nombre="Julia",
        apellido="Campos",
        dni="40000888",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta="2026-03-01",
        fecha_inicio_cobro="2026-03-01",
    )
    client.force_login(usuario)

    client.post(
        reverse("gestion:periodos_cuota"),
        {
            "action": "crear_periodo",
            "mes": "3",
            "ciclo_lectivo": str(ciclo.pk),
            "importe": "3000.00",
            "importe_recargo_mes": "500.00",
            "importe_recargo_mes_siguiente": "500.00",
            "fecha_vencimiento": "2026-03-10",
            "activo": "on",
        },
    )
    periodo = PeriodoCuota.objects.get(ciclo_lectivo=ciclo, mes=3)
    client.post(
        reverse("gestion:periodos_cuota"),
        {"action": "generar_cuotas", "periodo_id": str(periodo.pk)},
    )

    evento_periodo = EventoAuditoria.objects.get(entidad="cuotas.PeriodoCuota")
    evento_cuota = EventoAuditoria.objects.get(
        entidad="cuotas.Cuota",
        cambios__asociado__nuevo__id=asociado.pk,
    )
    assert evento_periodo.actor == usuario
    assert evento_cuota.actor == usuario
