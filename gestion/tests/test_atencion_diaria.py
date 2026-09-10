from datetime import date, datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.urls import reverse
from django.utils import timezone

from asociados.models import Asociado, CicloLectivo
from auditoria.models import EventoAuditoria
from cuotas.models import Cuota, Donacion, Pago, PagoCuota, PeriodoCuota

HOY = date(2026, 9, 30)


@pytest.fixture(autouse=True)
def fijar_hoy(monkeypatch):
    original = timezone.localdate
    monkeypatch.setattr(timezone, "localdate", lambda value=None, timezone=None: HOY if value is None else original(value, timezone))


def usuario(nombre="ana", equipo=False, consultar=False):
    user = get_user_model().objects.create_user(nombre)
    codenames = ["ver_atencion_diaria"]
    if equipo:
        codenames.append("ver_cobros_equipo")
    if consultar:
        codenames += ["consultar_asociados", "consultar_solicitudes_asociacion"]
    user.user_permissions.add(*Permission.objects.filter(content_type__app_label="gestion", codename__in=codenames))
    return user


def persona(dni="1", fecha=HOY):
    return Asociado.objects.create(nombre="Persona", apellido=f"Ejemplo {dni}", dni=dni,
        tipo=Asociado.TIPO_ADHERENTE, fecha_alta=fecha, fecha_inicio_cobro=fecha)


def pago(asociado, operador, importe="100", fecha=HOY, metodo=Pago.METODO_EFECTIVO):
    return Pago.objects.create(asociado=asociado, registrado_por=operador,
        importe=importe, fecha=fecha, metodo=metodo)


def auditar(pago, fecha):
    evento = EventoAuditoria.objects.create(
        entidad="cuotas.Pago", objeto_id=str(pago.pk), objeto_descripcion=str(pago),
        accion=EventoAuditoria.ACCION_CREAR, actor_etiqueta="Operador",
        origen=EventoAuditoria.ORIGEN_GESTION,
    )
    EventoAuditoria.objects.filter(pk=evento.pk).update(fecha=fecha)


@pytest.mark.parametrize("hoy,desde", [(HOY, date(2026,9,28)), (date(2026,9,28),date(2026,9,28)), (date(2026,10,4),date(2026,9,28)), (date(2026,1,1),date(2025,12,29))])
def test_semana_arranca_lunes(hoy, desde):
    from gestion.periodos import resolver_periodo_atencion
    periodo = resolver_periodo_atencion("esta_semana", hoy=hoy)
    assert (periodo.desde, periodo.hasta) == (desde, hoy)


def test_hoy_y_ayer_en_cambio_de_anio():
    from gestion.periodos import resolver_periodo_atencion
    assert resolver_periodo_atencion("ayer", hoy=date(2026,1,1)).desde == date(2025,12,31)
    assert resolver_periodo_atencion("hoy", hoy=HOY).hasta == HOY


@pytest.mark.parametrize("desde,hasta", [(None,HOY),(HOY,None),(HOY,date(2026,9,29)),(HOY,date(2026,10,1))])
def test_rango_invalido(desde, hasta):
    from gestion.periodos import resolver_periodo_atencion
    with pytest.raises(ValueError):
        resolver_periodo_atencion("personalizado", desde, hasta, hoy=HOY)


@pytest.mark.django_db
def test_totales_no_duplican_aplicaciones_ni_donaciones():
    from gestion.periodos import Periodo
    from gestion.selectors_atencion import pagos_del_periodo, resumir_pagos
    user = usuario()
    asociado = persona()
    p = pago(asociado, user, "160")
    ciclo = CicloLectivo.objects.create(anio=2026)
    for mes in (8,9):
        periodo = PeriodoCuota.objects.create(ciclo_lectivo=ciclo, mes=mes,
            importe=50, fecha_vencimiento=date(2026,mes,10))
        cuota = Cuota.objects.create(asociado=asociado, periodo=periodo, importe=50)
        PagoCuota.objects.create(pago=p, cuota=cuota, importe=70)  # Incluye mora.
    for importe in (5,15):
        Donacion.objects.create(pago=p, asociado=asociado, fecha=HOY, importe=importe)
    donacion = pago(asociado, user, "30", metodo=Pago.METODO_BILLETERA)
    Donacion.objects.create(pago=donacion, asociado=asociado, fecha=HOY, importe=30)
    pago(asociado, user, "999", fecha=date(2026,9,29))
    pagos = pagos_del_periodo(user, Periodo(HOY,HOY))
    datos = resumir_pagos(pagos)
    assert datos["total"] == Decimal("190")
    assert datos["efectivo"] == Decimal("160")
    assert datos["billetera"] == Decimal("30")
    assert datos["cantidad"] == 2
    assert datos["cuotas_recargos"] == Decimal("140")
    assert datos["donaciones"] == Decimal("50")
    assert datos["diferencia"] == 0


@pytest.mark.django_db
def test_cobros_propios_y_equipo_no_se_eluden():
    from gestion.periodos import Periodo
    from gestion.selectors_atencion import pagos_del_periodo
    a, b, admin = usuario(), usuario("sofia"), usuario("admin", equipo=True)
    asociado = persona()
    propio, ajeno = pago(asociado,a), pago(asociado,b)
    sin_operador = pago(asociado,None)
    periodo = Periodo(HOY,HOY)
    assert set(pagos_del_periodo(a,periodo,equipo=True).values_list("id",flat=True)) == {propio.id}
    assert set(pagos_del_periodo(admin,periodo,equipo=True).values_list("id",flat=True)) == {propio.id,ajeno.id,sin_operador.id}


@pytest.mark.django_db
def test_carga_auditada_y_fecha_efectiva_respetan_dia_local():
    from gestion.periodos import Periodo
    from gestion.selectors_atencion import pagos_cargados_con_otra_fecha, pagos_del_periodo
    user = usuario()
    asociado = persona()
    p = pago(asociado,user,fecha=date(2026,9,29))
    # 02:30 UTC es 23:30 del 29 en Argentina, no es una carga del 30.
    auditar(p,datetime(2026,9,30,2,30,tzinfo=ZoneInfo("UTC")))
    atrasado = pago(asociado,user,fecha=date(2026,9,29))
    auditar(atrasado,datetime(2026,9,30,12,tzinfo=ZoneInfo("UTC")))
    desconocido = pago(asociado,user,fecha=date(2026,9,29))
    assert not pagos_del_periodo(user,Periodo(HOY,HOY)).exists()
    with timezone.override("America/Argentina/Buenos_Aires"):
        ids = set(pagos_cargados_con_otra_fecha(user,Periodo(HOY,HOY)).values_list("id",flat=True))
    assert ids == {atrasado.id}


@pytest.mark.django_db
def test_sin_pagos_e_inconsistencias_visibles():
    from gestion.periodos import Periodo
    from gestion.selectors_atencion import pagos_del_periodo, resumir_pagos
    user = usuario()
    assert resumir_pagos(pagos_del_periodo(user,Periodo(HOY,HOY)))["total"] == 0
    pago(persona(),user,"100")  # Importe sin aplicación conocida: no inferir cuota.
    datos = resumir_pagos(pagos_del_periodo(user,Periodo(HOY,HOY)))
    assert datos["cuotas_recargos"] == 0
    assert datos["diferencia"] == 100
    assert datos["inconsistentes"] == 1


@pytest.mark.django_db
def test_vista_permiso_y_filtros_invalidos(client):
    url = reverse("gestion:atencion_diaria")
    assert client.get(url).status_code in (302,403)
    staff = get_user_model().objects.create_user("staff",is_staff=True)
    client.force_login(staff)
    assert client.get(url).status_code == 403
    user = usuario()
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200
    assert "no-store" in response.headers["Cache-Control"]
    for params in ({"operador":"equipo"},{"periodo":"personalizado","desde":"error"},{"periodo":"inventado"}):
        response = client.get(url,params)
        assert response.context["form"].errors
        assert "resumen" not in response.context


@pytest.mark.django_db
def test_detalle_de_pago_no_expone_ajenos(client):
    user, otro = usuario(), usuario("otro")
    propio, ajeno = pago(persona(),user), pago(persona("2"),otro)
    client.force_login(user)
    assert client.get(reverse("gestion:atencion_pago",args=[propio.id])).status_code == 200
    assert client.get(reverse("gestion:atencion_pago",args=[ajeno.id])).status_code == 404
    assert client.get(reverse("gestion:atencion_altas")).status_code == 403


@pytest.mark.django_db
def test_listado_pagina_y_preserva_filtros(client):
    user = usuario(equipo=True)
    asociado = persona()
    Pago.objects.bulk_create([Pago(asociado=asociado,registrado_por=user,fecha=HOY,importe=1,metodo=Pago.METODO_EFECTIVO) for _ in range(27)])
    client.force_login(user)
    response = client.get(reverse("gestion:atencion_diaria"),{"periodo":"personalizado","desde":"2026-09-30","hasta":"2026-09-30","operador":"equipo","page":2})
    assert response.context["resumen"]["cantidad"] == 27
    assert len(response.context["page_obj"]) == 2
    assert "operador=equipo" in response.context["querystring"]


@pytest.mark.django_db
def test_queries_acotadas_al_crecer_los_pagos(client, django_assert_max_num_queries):
    user = usuario(equipo=True, consultar=True)
    asociado = persona()
    Pago.objects.bulk_create([Pago(asociado=asociado, registrado_por=user, fecha=HOY,
        importe=1, metodo=Pago.METODO_EFECTIVO) for _ in range(60)])
    client.force_login(user)
    with django_assert_max_num_queries(18):
        response = client.get(reverse("gestion:atencion_diaria"))
        assert response.status_code == 200
        assert len(response.context["page_obj"]) == 25
        assert response.context["resumen"]["cantidad"] == 60


@pytest.mark.django_db
def test_los_permisos_ocultan_bloques_y_altas_no_filtran_por_cobrador(client):
    user = usuario()
    persona("1")
    persona("2",fecha=date(2026,9,29))
    client.force_login(user)
    response = client.get(reverse("gestion:atencion_diaria"))
    assert "altas" not in response.context
    assert "solicitudes" not in response.context
    assert reverse("gestion:solicitudes_asociacion") not in response.content.decode()
    user.user_permissions.add(*Permission.objects.filter(content_type__app_label="gestion", codename__in=["consultar_asociados","consultar_solicitudes_asociacion"]))
    response = client.get(reverse("gestion:atencion_diaria"))
    assert response.context["altas"]["total"] == 1
    assert len(response.context["solicitudes"]) == 3
    response = client.get(reverse("gestion:atencion_altas"))
    assert [a.dni for a in response.context["page_obj"]] == ["1"]


@pytest.mark.django_db
def test_solicitudes_abiertas_de_todo_el_equipo_sin_filtro_temporal(client):
    from asociados.models import SolicitudAsociacion
    user = usuario(consultar=True)
    for i, estado in enumerate(["recibida","recibida","observada","datos_aprobados","alta_completada","cancelada"]):
        SolicitudAsociacion.objects.create(nombre="Ejemplo",apellido="Persona",dni=str(45000000+i),
            email="prueba@example.test",telefono="12345678",direccion="Calle 1",es_estudiante_cet3=False,
            estado=estado,token_seguimiento_hash=f"{i:064x}",token_seguimiento_vence_en=timezone.now())
    client.force_login(user)
    response = client.get(reverse("gestion:atencion_diaria"),{"periodo":"ayer"})
    assert {s["estado"]:s["cantidad"] for s in response.context["solicitudes"]} == {"recibida":2,"observada":1,"datos_aprobados":1}


@pytest.mark.django_db
def test_advertencia_importacion_y_primera_carga_sin_inventar(client):
    from gestion.periodos import Periodo
    from gestion.selectors_atencion import con_fecha_carga, pagos_cargados_con_otra_fecha
    user = usuario()
    p = pago(persona(),user)
    p.observaciones = "Importado desde planilla historica de cuotas. Fila original 2."
    p.save()
    assert con_fecha_carga(Pago.objects.filter(pk=p.pk)).get().registrado_en is None
    client.force_login(user)
    response = client.get(reverse("gestion:atencion_diaria"))
    assert response.context["resumen"]["fechas_convencionales"] == 1
    assert "Pagos históricos importados" in response.content.decode()
    auditar(p,datetime(2026,9,29,12,tzinfo=ZoneInfo("UTC")))
    auditar(p,datetime(2026,9,30,12,tzinfo=ZoneInfo("UTC")))
    assert not pagos_cargados_con_otra_fecha(user,Periodo(HOY,HOY)).exists()


@pytest.mark.django_db
def test_retorno_local_del_detalle_y_cache_en_rutas_secundarias(client):
    user = usuario(consultar=True)
    p = pago(persona(),user)
    client.force_login(user)
    detalle = reverse("gestion:atencion_pago",args=[p.pk])
    for target in ("https://externo.example/", "//externo.example/", "/gestion/asociados/", "http://["):
        response = client.get(detalle,{"volver":target})
        assert response.context["tablero_url"] == reverse("gestion:atencion_diaria")
        assert "no-store" in response.headers["Cache-Control"]
    for name in ("atencion_altas","atencion_cargas"):
        assert "no-store" in client.get(reverse("gestion:"+name)).headers["Cache-Control"]


@pytest.mark.django_db
def test_migracion_y_matriz_asignan_solo_los_permisos_previstos():
    from importlib import import_module
    from django.apps import apps
    from django.contrib.auth.models import Group
    from django.db import connection
    from usuarios.group_configuration import sync_group_configuration
    from usuarios.roles import ATENCION_ASOCIADO_GROUP, ADMINISTRADOR_MUTUAL_GROUP
    Group.objects.get_or_create(name=ATENCION_ASOCIADO_GROUP)
    Group.objects.get_or_create(name=ADMINISTRADOR_MUTUAL_GROUP)
    migration = import_module("gestion.migrations.0008_permisos_atencion_diaria")
    # Solo usa la conexión para elegir el alias, no modifica esquema.
    from types import SimpleNamespace
    migration.asignar_permisos(apps, SimpleNamespace(connection=connection))
    migration.asignar_permisos(apps, SimpleNamespace(connection=connection))
    atencion = Group.objects.get(name=ATENCION_ASOCIADO_GROUP)
    admin = Group.objects.get(name=ADMINISTRADOR_MUTUAL_GROUP)
    assert atencion.permissions.filter(codename="ver_atencion_diaria").exists()
    assert not atencion.permissions.filter(codename="ver_cobros_equipo").exists()
    assert admin.permissions.filter(codename="ver_cobros_equipo").exists()
    sync_group_configuration()
    assert not atencion.permissions.filter(codename="ver_cobros_equipo").exists()
    assert admin.permissions.filter(codename="ver_atencion_diaria").exists()


@pytest.mark.django_db
def test_centavos_no_generan_falsas_inconsistencias(client):
    from gestion.periodos import Periodo
    from gestion.selectors_atencion import pagos_del_periodo, resumir_pagos
    user = usuario()
    asociado = persona()
    p = pago(asociado,user,"0.30")
    for importe in ("0.10","0.20"):
        Donacion.objects.create(pago=p,asociado=asociado,fecha=HOY,importe=importe)
    datos = resumir_pagos(pagos_del_periodo(user,Periodo(HOY,HOY)))
    assert datos["inconsistentes"] == 0
    assert datos["donaciones"] == Decimal("0.30")
    assert datos["diferencia"] == Decimal("0.00")
    client.force_login(user)
    response = client.get(reverse("gestion:atencion_pago",args=[p.pk]))
    assert response.context["diferencia"] == 0


@pytest.mark.django_db
def test_limites_inclusivos_de_pago():
    from gestion.periodos import Periodo
    from gestion.selectors_atencion import pagos_del_periodo
    user = usuario()
    a = persona()
    for day in (27,28,29,30):
        pago(a,user,fecha=date(2026,9,day))
    assert list(pagos_del_periodo(user,Periodo(date(2026,9,28),date(2026,9,29))).order_by("fecha").values_list("fecha",flat=True)) == [date(2026,9,28),date(2026,9,29)]


@pytest.mark.django_db
@pytest.mark.parametrize("permiso,visible,oculto", [("consultar_asociados","altas","solicitudes"),("consultar_solicitudes_asociacion","solicitudes","altas")])
def test_bloques_con_permisos_independientes(client, permiso, visible, oculto):
    user = usuario()
    user.user_permissions.add(Permission.objects.get(codename=permiso,content_type__app_label="gestion"))
    client.force_login(user)
    response = client.get(reverse("gestion:atencion_diaria"))
    assert visible in response.context
    assert oculto not in response.context


@pytest.mark.django_db
def test_permiso_equipo_no_da_acceso_al_tablero(client):
    user = usuario(equipo=True)
    user.user_permissions.remove(Permission.objects.get(codename="ver_atencion_diaria",content_type__app_label="gestion"))
    client.force_login(user)
    assert client.get(reverse("gestion:atencion_diaria")).status_code == 403


@pytest.mark.django_db
def test_modificacion_auditada_no_es_fecha_de_carga():
    from gestion.selectors_atencion import con_fecha_carga
    user = usuario()
    p = pago(persona(),user)
    EventoAuditoria.objects.create(entidad="cuotas.Pago",objeto_id=str(p.pk),
        objeto_descripcion=str(p),accion=EventoAuditoria.ACCION_MODIFICAR,
        actor_etiqueta="Operador",origen=EventoAuditoria.ORIGEN_ADMIN)
    assert con_fecha_carga(Pago.objects.filter(pk=p.pk)).get().registrado_en is None
