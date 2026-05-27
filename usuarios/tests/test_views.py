import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils import timezone

from asociados.services import create_asociado
from contabilidad.models import CuentaContable
from comercios.models import BeneficioComercio, Comercio
from cuotas.models import Pago, PeriodoCuota
from cuotas.services import generar_cuotas_para_periodo, registrar_pago
from usuarios.services import COMERCIO_GROUP


def crear_cuentas_contables_basicas():
    CuentaContable.objects.create(
        codigo="1.1.01",
        nombre="Caja",
        tipo=CuentaContable.TIPO_ACTIVO,
    )
    CuentaContable.objects.create(
        codigo="1.1.02",
        nombre="Billetera virtual",
        tipo=CuentaContable.TIPO_ACTIVO,
    )
    CuentaContable.objects.create(
        codigo="4.1.01",
        nombre="Ingresos por cuotas",
        tipo=CuentaContable.TIPO_INGRESO,
    )


@pytest.mark.django_db
def test_login_redirige_a_panel_asociado(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="aso", password="secreto123")
    asociado = create_asociado(
        nombre="Ana",
        apellido="Perez",
        dni="40111999",
        tipo="asociado",
        fecha_alta="2026-05-10",
    )
    asociado.usuario = user
    asociado.save(update_fields=["usuario"])

    response = client.post(
        reverse("usuarios:login"),
        {"username": "aso", "password": "secreto123"},
    )

    assert response.status_code == 302
    assert response.url == reverse("asociados:dashboard")


@pytest.mark.django_db
def test_login_redirige_a_panel_comercio(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="com", password="secreto123")
    Comercio.objects.create(nombre="Libreria Sur", direccion="Mitre 123", usuario=user)

    response = client.post(
        reverse("usuarios:login"),
        {"username": "com", "password": "secreto123"},
    )

    assert response.status_code == 302
    assert response.url == reverse("comercios:dashboard")


@pytest.mark.django_db
def test_login_usuario_con_grupo_comercio_sin_perfil_redirige_a_home(client):
    group = Group.objects.create(name=COMERCIO_GROUP)
    user_model = get_user_model()
    user = user_model.objects.create_user(username="com_sin_perfil", password="secreto123")
    user.groups.add(group)

    response = client.post(
        reverse("usuarios:login"),
        {"username": "com_sin_perfil", "password": "secreto123"},
    )

    assert response.status_code == 302
    assert response.url == reverse("contenidos:home")


@pytest.mark.django_db
def test_login_staff_redirige_a_dashboard_de_gestion(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(
        username="admin_gestion",
        password="secreto123",
        is_staff=True,
    )

    response = client.post(
        reverse("usuarios:login"),
        {"username": "admin_gestion", "password": "secreto123"},
    )

    assert response.status_code == 302
    assert response.url == reverse("usuarios:gestion_dashboard")


@pytest.mark.django_db
def test_dashboard_gestion_requiere_staff(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="aso_sin_staff", password="secreto123")
    client.force_login(user)

    response = client.get(reverse("usuarios:gestion_dashboard"))

    assert response.status_code == 403


@pytest.mark.django_db
def test_dashboard_gestion_muestra_metricas_basicas(client):
    user_model = get_user_model()
    staff = user_model.objects.create_user(
        username="staff1",
        password="secreto123",
        is_staff=True,
    )
    user_con_acceso = user_model.objects.create_user(username="aso_login", password="secreto123")
    user_con_acceso.last_login = timezone.now()
    user_con_acceso.save(update_fields=["last_login"])

    asociado_con_usuario = create_asociado(
        nombre="Laura",
        apellido="Mendez",
        dni="41111999",
        tipo="asociado",
        fecha_alta="2026-05-10",
    )
    asociado_con_usuario.usuario = user_con_acceso
    asociado_con_usuario.save(update_fields=["usuario"])

    create_asociado(
        nombre="Mario",
        apellido="Sosa",
        dni="42222999",
        tipo="asociado",
        fecha_alta="2026-05-10",
    )

    asociado_deudor = create_asociado(
        nombre="Nina",
        apellido="Ruiz",
        dni="43333999",
        tipo="asociado",
        fecha_alta="2026-05-10",
    )

    crear_cuentas_contables_basicas()

    periodo = PeriodoCuota.objects.create(
        mes=timezone.localdate().month,
        anio=timezone.localdate().year,
        importe="3000.00",
        importe_recargo_mora="500.00",
        fecha_vencimiento=timezone.localdate(),
    )
    generar_cuotas_para_periodo(periodo)
    registrar_pago(
        asociado=asociado_con_usuario,
        fecha=timezone.localdate(),
        importe="3000.00",
        metodo=Pago.METODO_EFECTIVO,
    )

    comercio = Comercio.objects.create(nombre="Libreria Norte", direccion="Mitre 321")
    BeneficioComercio.objects.create(
        comercio=comercio,
        titulo="10% en utiles",
        descripcion="Descuento para asociados",
        tipo_descuento=BeneficioComercio.TIPO_PORCENTAJE,
        valor_descuento="10.00",
        activo=True,
    )

    client.force_login(staff)
    response = client.get(reverse("usuarios:gestion_dashboard"))

    assert response.status_code == 200
    assert response.context["resumen"]["asociados_activos"] == 3
    assert response.context["resumen"]["asociados_sin_usuario"] == 2
    assert response.context["resumen"]["deudores"] == 2
    assert response.context["resumen"]["cuotas_pagadas"] == 1
    assert response.context["resumen"]["beneficios_vigentes"] == 1
    assert any(item["asociado"] == asociado_deudor for item in response.context["deudores"])


@pytest.mark.django_db
def test_cobros_gestion_requiere_staff(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="no_staff", password="secreto123")
    client.force_login(user)

    response = client.get(reverse("usuarios:gestion_cobros"))

    assert response.status_code == 403


@pytest.mark.django_db
def test_deudores_gestion_requiere_staff(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="no_staff_deuda", password="secreto123")
    client.force_login(user)

    response = client.get(reverse("usuarios:gestion_deudores"))

    assert response.status_code == 403


@pytest.mark.django_db
def test_periodos_cuota_gestion_requiere_staff(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="no_staff_periodos", password="secreto123")
    client.force_login(user)

    response = client.get(reverse("usuarios:gestion_periodos_cuota"))

    assert response.status_code == 403


@pytest.mark.django_db
def test_asociados_gestion_requiere_staff(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="no_staff_asoc", password="secreto123")
    client.force_login(user)

    response = client.get(reverse("usuarios:gestion_asociados"))

    assert response.status_code == 403


@pytest.mark.django_db
def test_cobros_gestion_busca_asociado_y_registra_pago(client):
    user_model = get_user_model()
    staff = user_model.objects.create_user(username="staff_cobro", password="secreto123", is_staff=True)
    asociado = create_asociado(
        nombre="Paula",
        apellido="Gimenez",
        dni="45555111",
        tipo="asociado",
        fecha_alta="2026-05-10",
    )
    crear_cuentas_contables_basicas()
    periodo = PeriodoCuota.objects.create(
        mes=timezone.localdate().month,
        anio=timezone.localdate().year,
        importe="3000.00",
        importe_recargo_mora="0.00",
        fecha_vencimiento=timezone.localdate(),
    )
    generar_cuotas_para_periodo(periodo)

    client.force_login(staff)

    response_busqueda = client.get(reverse("usuarios:gestion_cobros"), {"q": "45555111"})
    assert response_busqueda.status_code == 200
    assert "Gimenez" in response_busqueda.content.decode()

    response_cobro = client.post(
        reverse("usuarios:gestion_cobros"),
        {
            "asociado_id": asociado.id,
            "fecha": timezone.localdate().isoformat(),
            "importe": "3000.00",
            "metodo": Pago.METODO_EFECTIVO,
            "observaciones": "Pago en mostrador",
        },
        follow=True,
    )

    assert response_cobro.status_code == 200
    assert Pago.objects.filter(asociado=asociado, importe="3000.00").exists()
    cuota = asociado.cuotas.get(periodo=periodo)
    assert cuota.estado == cuota.ESTADO_PAGADA
    assert "registrado para Gimenez, Paula" in response_cobro.content.decode()


@pytest.mark.django_db
def test_cobros_gestion_muestra_error_si_supera_deuda(client):
    user_model = get_user_model()
    staff = user_model.objects.create_user(username="staff_error", password="secreto123", is_staff=True)
    asociado = create_asociado(
        nombre="Ivan",
        apellido="Molina",
        dni="46666111",
        tipo="asociado",
        fecha_alta="2026-05-10",
    )
    crear_cuentas_contables_basicas()
    periodo = PeriodoCuota.objects.create(
        mes=timezone.localdate().month,
        anio=timezone.localdate().year,
        importe="3000.00",
        importe_recargo_mora="0.00",
        fecha_vencimiento=timezone.localdate(),
    )
    generar_cuotas_para_periodo(periodo)

    client.force_login(staff)
    response = client.post(
        reverse("usuarios:gestion_cobros"),
        {
            "asociado_id": asociado.id,
            "fecha": timezone.localdate().isoformat(),
            "importe": "4000.00",
            "metodo": Pago.METODO_EFECTIVO,
            "observaciones": "",
        },
    )

    assert response.status_code == 200
    assert "no puede superar la deuda" in response.content.decode()
    assert Pago.objects.count() == 0


@pytest.mark.django_db
def test_deudores_gestion_lista_asociados_y_linkea_a_cobro(client):
    user_model = get_user_model()
    staff = user_model.objects.create_user(username="staff_deudores", password="secreto123", is_staff=True)
    asociado = create_asociado(
        nombre="Lucia",
        apellido="Ramos",
        dni="47777111",
        tipo="asociado",
        fecha_alta="2026-05-10",
    )
    crear_cuentas_contables_basicas()
    periodo = PeriodoCuota.objects.create(
        mes=timezone.localdate().month,
        anio=timezone.localdate().year,
        importe="3000.00",
        importe_recargo_mora="0.00",
        fecha_vencimiento=timezone.localdate(),
    )
    generar_cuotas_para_periodo(periodo)

    client.force_login(staff)
    response = client.get(reverse("usuarios:gestion_deudores"))

    assert response.status_code == 200
    content = response.content.decode()
    assert "Ramos" in content
    assert f'?asociado={asociado.id}' in content


@pytest.mark.django_db
def test_periodos_cuota_gestion_crea_periodo(client):
    user_model = get_user_model()
    staff = user_model.objects.create_user(username="staff_periodo", password="secreto123", is_staff=True)
    client.force_login(staff)

    response = client.post(
        reverse("usuarios:gestion_periodos_cuota"),
        {
            "action": "crear_periodo",
            "mes": 6,
            "anio": 2026,
            "importe": "3200.00",
            "importe_recargo_mora": "500.00",
            "fecha_vencimiento": "2026-06-10",
            "activo": "on",
        },
        follow=True,
    )

    assert response.status_code == 200
    assert PeriodoCuota.objects.filter(mes=6, anio=2026, importe="3200.00").exists()
    assert "Periodo 06/2026 creado correctamente" in response.content.decode()


@pytest.mark.django_db
def test_periodos_cuota_gestion_genera_cuotas_sin_duplicar(client):
    user_model = get_user_model()
    staff = user_model.objects.create_user(username="staff_generacion", password="secreto123", is_staff=True)
    create_asociado(
        nombre="Lara",
        apellido="Suarez",
        dni="48888111",
        tipo="asociado",
        fecha_alta="2026-05-10",
    )
    create_asociado(
        nombre="Nico",
        apellido="Ferreyra",
        dni="49999111",
        tipo="asociado",
        fecha_alta="2026-05-20",
    )
    periodo = PeriodoCuota.objects.create(
        mes=6,
        anio=2026,
        importe="3200.00",
        importe_recargo_mora="500.00",
        fecha_vencimiento="2026-06-10",
    )

    client.force_login(staff)

    primer_response = client.post(
        reverse("usuarios:gestion_periodos_cuota"),
        {"action": "generar_cuotas", "periodo_id": periodo.id},
        follow=True,
    )
    assert primer_response.status_code == 200
    assert periodo.cuotas.count() == 2
    assert "2 cuotas creadas" in primer_response.content.decode()

    segunda_response = client.post(
        reverse("usuarios:gestion_periodos_cuota"),
        {"action": "generar_cuotas", "periodo_id": periodo.id},
        follow=True,
    )
    assert segunda_response.status_code == 200
    assert periodo.cuotas.count() == 2
    assert "0 cuotas creadas" in segunda_response.content.decode()


@pytest.mark.django_db
def test_asociados_gestion_busca_y_muestra_detalle(client):
    user_model = get_user_model()
    staff = user_model.objects.create_user(username="staff_asoc", password="secreto123", is_staff=True)
    asociado = create_asociado(
        nombre="Julia",
        apellido="Campos",
        dni="40000111",
        tipo="asociado",
        fecha_alta="2026-05-10",
    )

    client.force_login(staff)
    listado = client.get(reverse("usuarios:gestion_asociados"), {"q": "Campos"})

    assert listado.status_code == 200
    assert "Campos" in listado.content.decode()

    detalle = client.get(reverse("usuarios:gestion_asociado_detalle", args=[asociado.id]))

    assert detalle.status_code == 200
    content = detalle.content.decode()
    assert "Julia" in content
    assert "Sin usuario" in content
    assert f'?asociado={asociado.id}' in content


@pytest.mark.django_db
def test_asociado_detalle_permite_editar_fecha_inicio_cobro(client):
    user_model = get_user_model()
    staff = user_model.objects.create_user(username="staff_edita_asoc", password="secreto123", is_staff=True)
    asociado = create_asociado(
        nombre="Milena",
        apellido="Armada",
        dni="30000111",
        tipo="asociado",
        fecha_alta="2026-05-22",
    )

    client.force_login(staff)
    response = client.post(
        reverse("usuarios:gestion_asociado_detalle", args=[asociado.id]),
        {
            "nombre": "Milena",
            "apellido": "Armada",
            "dni": "30000111",
            "email": "milena@example.com",
            "telefono": "123456",
            "tipo": "asociado",
            "curso_actual": "",
            "estado": "activo",
            "fecha_alta": "2026-05-22",
            "fecha_inicio_cobro": "2026-05-01",
            "fecha_baja": "",
            "motivo_baja": "",
        },
        follow=True,
    )

    assert response.status_code == 200
    asociado.refresh_from_db()
    assert str(asociado.fecha_inicio_cobro) == "2026-05-01"
    assert asociado.email == "milena@example.com"
    assert "Asociado actualizado correctamente" in response.content.decode()
