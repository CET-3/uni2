from datetime import date
from decimal import Decimal

import pytest
from django.utils import timezone

from asociados.models import Asociado, CicloLectivo
from cuotas.models import Cuota, Donacion, Pago, PagoCuota, PeriodoCuota
from gestion.periodos import Periodo

HOY = date(2026, 9, 30)


def persona(dni, alta=date(2026, 1, 1), baja=None, tipo="asociado"):
    return Asociado.objects.create(dni=dni, nombre="Persona", apellido=dni, tipo=tipo,
        fecha_alta=alta, fecha_inicio_cobro=alta, fecha_baja=baja,
        estado="inactivo" if baja else "activo")


def cuota(persona, mes, importe=100, pagado=0):
    ciclo, _ = CicloLectivo.objects.get_or_create(anio=2026)
    periodo, _ = PeriodoCuota.objects.get_or_create(ciclo_lectivo=ciclo, mes=mes,
        defaults={"importe": 100, "fecha_vencimiento": date(2026, mes, 10)})
    return Cuota.objects.create(asociado=persona, periodo=periodo, importe=importe, importe_pagado=pagado,
        importe_recargo_mes=10, importe_recargo_mes_siguiente=20,
        estado="pagada" if pagado >= importe else "pendiente")


def pagar(cuota, fecha, importe, historico=False):
    pago = Pago.objects.create(asociado=cuota.asociado, fecha=fecha, importe=importe, metodo="efectivo",
        observaciones="Importado desde planilla historica de cuotas." if historico else "")
    PagoCuota.objects.create(pago=pago, cuota=cuota, importe=importe)
    cuota.importe_pagado = importe
    cuota.save(update_fields=["importe_pagado"])
    return pago


@pytest.mark.django_db
def test_padron_historico_no_usa_estado_actual():
    from gestion.selectors_metricas import metricas_padron
    persona("1")
    persona("2", alta=date(2026, 8, 15))
    persona("3", baja=date(2026, 8, 20))
    persona("4", baja=date(2026, 9, 15))
    resultado = metricas_padron(Periodo(date(2026, 8, 1), date(2026, 8, 31)))
    assert (resultado["activos"], resultado["altas"], resultado["bajas"]) == (3, 1, 1)
    assert resultado["serie"][-1]["activos"] == 3


@pytest.mark.django_db
def test_cuotas_reales_y_cobros_tardios_no_son_ingresos_del_periodo():
    from gestion.selectors_metricas import metricas_cuotas, metricas_ingresos
    asociado = persona("1")
    agosto = cuota(asociado, 8)
    septiembre = cuota(asociado, 9, importe=50)
    cuota(persona("2"), 9, importe=0)
    cuota(persona("3"), 9, importe=100)
    pagar(agosto, date(2026, 9, 15), 130)
    pagar(septiembre, date(2026, 9, 20), 60)
    rango = Periodo(date(2026, 9, 1), HOY)
    resultado = metricas_cuotas(rango, hoy=HOY)
    assert (resultado["generado"], resultado["cobrado"], resultado["pendiente"]) == (150, 50, 100)
    assert resultado["cumplimiento"] == Decimal("33.3")
    assert metricas_ingresos(rango)["total"] == 190
    assert resultado["personas_saldadas"] == 2


@pytest.mark.django_db
def test_importado_paga_cuota_sin_sumar_ingreso_y_pago_posterior_se_incluye():
    from gestion.selectors_metricas import metricas_cuotas, metricas_ingresos
    p = persona("1")
    pagar(cuota(p, 8), date(2026, 9, 15), 130, historico=True)
    rango = Periodo(date(2026, 8, 1), date(2026, 8, 31))
    assert metricas_cuotas(rango, hoy=HOY)["cobrado"] == 100
    assert metricas_ingresos(Periodo(date(2026, 9, 1), HOY))["total"] == 0


@pytest.mark.django_db
def test_deuda_actual_con_recargos_y_grupos():
    from gestion.selectors_metricas import metricas_deuda
    a, b = persona("1"), persona("2", tipo="adherente")
    for mes in (7, 8, 9):
        cuota(a, mes)
    cuota(b, 9)
    deuda = metricas_deuda(hoy=HOY)
    assert (deuda["personas"], deuda["cuotas"], deuda["total"]) == (2, 4, 480)
    assert deuda["grupos"][2]["personas"] == 1
    assert deuda["grupos"][2]["total"] == 370


@pytest.mark.django_db
def test_periodo_vacio_y_filtro_tipo():
    from gestion.selectors_metricas import metricas_cuotas, metricas_padron
    persona("1", tipo="adherente")
    rango = Periodo(date(2026, 9, 1), HOY)
    assert metricas_cuotas(rango, hoy=HOY)["cumplimiento"] is None
    assert metricas_padron(rango, tipo="asociado")["activos"] == 0


def test_variacion_sin_base_y_sentido():
    from gestion.services_metricas import variacion
    assert variacion(10, 0)["porcentaje"] is None
    assert variacion(10, 20)["clase"] == "text-danger"
    assert variacion(10, 20, favorable="baja")["clase"] == "text-success"
    assert variacion(0, 0)["flecha"] == "→"


@pytest.mark.django_db
def test_vista_permiso_filtros_y_json(client):
    from django.contrib.auth.models import User, Permission
    from django.urls import reverse
    user = User.objects.create_user("metricas")
    client.force_login(user)
    url = reverse("gestion:metricas")
    assert url == "/gestion/metricas/"
    assert client.get(url).status_code == 403
    user.user_permissions.add(Permission.objects.get(content_type__app_label="gestion", codename="ver_metricas"))
    response = client.get(url)
    assert response.status_code == 200
    assert "no-store" in response["Cache-Control"]
    assert b'application/json' in response.content
    assert b'chart.umd.js' in response.content
    assert client.get(url, {"tipo": "invalido"}).context["form"].errors
    assert client.get(reverse("gestion:metricas_detalle"), {"categoria": "altas"}).status_code == 403


@pytest.mark.django_db
def test_capital_saldado_con_centavos_no_crea_pendiente():
    from gestion.selectors_metricas import metricas_cuotas
    c = cuota(persona("1"), 9, importe=Decimal("0.80"))
    pagar(c, HOY, Decimal("0.10"))
    pagar(c, HOY, Decimal("0.70"))
    c.importe_pagado = Decimal("0.80")
    c.save()
    datos = metricas_cuotas(Periodo(date(2026, 9, 1), HOY), hoy=HOY)
    assert datos["personas_saldadas"] == 1
    assert datos["pendiente"] == 0


@pytest.mark.django_db
def test_activos_inconsistentes_no_inventan_historia():
    from gestion.selectors_metricas import metricas_padron
    p = persona("1")
    p.estado = "inactivo"
    p.save()
    resultado = metricas_padron(Periodo(date(2026, 9, 1), HOY))
    assert resultado["activos"] is None
    assert resultado["inconsistentes"] == 1


@pytest.mark.django_db
def test_consultas_no_crecen_con_el_padron(django_assert_num_queries):
    from django.db import connection
    from django.test.utils import CaptureQueriesContext
    from gestion.services_metricas import construir_metricas
    rango = Periodo(date(2026, 1, 1), HOY)
    with CaptureQueriesContext(connection) as primero:
        construir_metricas(rango, tipo="todos", hoy=HOY)
    for i in range(30):
        cuota(persona(str(i)), 9)
    with CaptureQueriesContext(connection) as segundo:
        construir_metricas(rango, tipo="todos", hoy=HOY)
    assert len(segundo) == len(primero)
    assert len(segundo) <= 25


@pytest.mark.django_db
def test_detalle_deuda_exige_permiso_y_filtra_personas(client):
    from django.contrib.auth.models import User, Permission
    from django.urls import reverse
    user = User.objects.create_user("detalle")
    user.user_permissions.add(*Permission.objects.filter(content_type__app_label="gestion", codename__in=["ver_metricas", "consultar_asociados"]))
    client.force_login(user)
    url = reverse("gestion:metricas_detalle")
    assert client.get(url, {"categoria": "deuda", "grupo": "3"}).status_code == 403
    user.user_permissions.add(Permission.objects.get(content_type__app_label="gestion", codename="ver_deudores"))
    a, b = persona("1"), persona("2")
    for mes in (5, 6, 7):
        cuota(a, mes)
    cuota(b, 8)
    response = client.get(url, {"categoria": "deuda", "grupo": "3"})
    assert response.status_code == 200
    assert list(response.context["page_obj"]) == [a]
    assert client.get(url, {"categoria": "deuda", "grupo": "500"}).status_code == 404
    assert "no-store" in response["Cache-Control"]


@pytest.mark.django_db
def test_solicitudes_cohorte_y_estado_actual():
    from datetime import datetime
    from zoneinfo import ZoneInfo
    from asociados.models import SolicitudAsociacion
    from gestion.selectors_metricas import metricas_solicitudes
    s = SolicitudAsociacion.objects.create(nombre="Ejemplo", apellido="Persona", dni="QA12345", email="qa@example.test", telefono="123456789", direccion="Ejemplo", es_estudiante_cet3=False, token_seguimiento_hash="a" * 64, token_seguimiento_vence_en=timezone.now(), estado="alta_completada")
    SolicitudAsociacion.objects.filter(pk=s.pk).update(creado_en=datetime(2026, 9, 1, 1, tzinfo=ZoneInfo("UTC")))
    agosto = metricas_solicitudes(Periodo(date(2026, 8, 1), date(2026, 8, 31)))
    assert (agosto["total"], agosto["conversion"]) == (1, 100)
    assert metricas_solicitudes(Periodo(date(2026, 9, 1), HOY))["total"] == 0


@pytest.mark.django_db
@pytest.mark.parametrize("dia,activas", [(10, 5), (11, 4)])
def test_credenciales_coinciden_con_validacion_y_excluyen_bajas(dia, activas):
    from cuotas.selectors import calcular_estado_credencial
    from gestion.selectors_metricas import metricas_credenciales

    sin_cuotas = persona("sin")
    cuota(persona("bonificada"), 8, importe=0)
    cuota(persona("pagada"), 8, pagado=100)
    cuota(persona("anterior", tipo="adherente"), 8, pagado=50)
    cuota(persona("actual"), 9)
    cuota(persona("futura", tipo="adherente"), 10)
    persona("baja", baja=date(2026, 8, 1))
    hoy = date(2026, 9, dia)
    datos = metricas_credenciales(hoy=hoy)
    assert datos["total"] == 6
    assert datos["activas"] == activas
    assert datos["inactivas"] == 6 - activas
    assert datos["activas"] == sum(calcular_estado_credencial(p, hoy).activa for p in Asociado.objects.all())
    adherentes = metricas_credenciales("adherente", hoy=hoy)
    assert (adherentes["total"], adherentes["activas"], adherentes["porcentaje"]) == (2, 1, 50)
    assert datos["por_tipo"][1]["inactivas"] == 1
    assert sin_cuotas.estado == "activo"


@pytest.mark.django_db
def test_credenciales_vacias_y_card_sin_comparacion_historica():
    from gestion.selectors_metricas import metricas_credenciales
    from gestion.services_metricas import construir_metricas
    assert metricas_credenciales(hoy=HOY)["porcentaje"] is None
    persona("actual", alta=date(2026, 9, 1))
    datos = construir_metricas(Periodo(date(2026, 8, 1), date(2026, 8, 31)), hoy=HOY)
    assert len(datos["cards"]) == 4
    assert datos["cards"][0]["titulo"] == "Padrón activo"
    assert datos["cards"][1]["valor"] == "1"
    assert datos["cards"][1]["cambio"] is None
    assert datos["proporciones"][0]["progreso"] == 100
    assert datos["proporciones"][1]["progreso"] is None


@pytest.mark.django_db
def test_proporciones_separan_personas_y_montos():
    from gestion.services_metricas import construir_metricas
    a = persona("1")
    pagar(cuota(a, 9), HOY, 100)
    cuota(persona("2"), 9, importe=300)
    datos = construir_metricas(Periodo(date(2026, 9, 1), HOY), hoy=HOY)
    personas, montos = datos["proporciones"]
    assert personas["progreso"] == 50
    assert personas["relacion"] == "1 de 2 personas de alta"
    assert montos["progreso"] == 25
    assert montos["relacion"] == "$ 100,00 cobrados de $ 400,00 generados"


@pytest.mark.django_db
def test_detalle_credenciales_deuda_exige_permisos_y_respeta_tipo(client, monkeypatch):
    from django.contrib.auth.models import User, Permission
    from django.urls import reverse
    monkeypatch.setattr(timezone, "localdate", lambda: HOY)
    user = User.objects.create_user("credenciales")
    user.user_permissions.add(*Permission.objects.filter(content_type__app_label="gestion", codename__in=["ver_metricas", "consultar_asociados"]))
    client.force_login(user)
    params = {"categoria": "credenciales", "estado": "inactivas", "tipo": "adherente"}
    url = reverse("gestion:metricas_detalle")
    assert client.get(url, params).status_code == 403
    user.user_permissions.add(Permission.objects.get(content_type__app_label="gestion", codename="ver_deudores"))
    a = persona("adherente", tipo="adherente")
    cuota(a, 8)
    cuota(persona("asociado"), 8)
    cuota(persona("baja", tipo="adherente", baja=date(2026, 8, 1)), 8)
    response = client.get(url, params)
    assert response.status_code == 200
    assert list(response.context["page_obj"]) == [a]
    assert "no-store" in response["Cache-Control"]
    assert client.get(url, {**params, "estado": "inventado"}).status_code == 404
