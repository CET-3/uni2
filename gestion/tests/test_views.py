import pytest
from io import BytesIO
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
from openpyxl import Workbook, load_workbook

from asociados.importers import PADRON_IMPORT_SESSION_KEY
from asociados.models import Asociado, CicloLectivo, Curso
from asociados.services import create_asociado
from contabilidad.models import Asiento, CuentaContable
from cuotas.models import Cuota, Pago, PagoCuota, PeriodoCuota
from cuotas.services import generar_cuotas_para_periodo, registrar_pago


def crear_cuentas_contables_basicas():
    CuentaContable.objects.create(codigo="1.1.01", nombre="Caja", tipo=CuentaContable.TIPO_ACTIVO)
    CuentaContable.objects.create(codigo="1.1.02", nombre="Billetera virtual", tipo=CuentaContable.TIPO_ACTIVO)
    CuentaContable.objects.create(codigo="4.1.01", nombre="Ingresos por cuotas", tipo=CuentaContable.TIPO_INGRESO)


def crear_planilla_padron(rows):
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "PADRÓN GENERAL"
    worksheet.append(
        [
            None,
            "Apellido/nombre",
            "Curso/división/Ciclo/turno",
            "CICLO",
            "Categoria (act./adh.)",
            "DNI",
            "Celular",
            "Mail",
            "Dirección",
        ]
    )
    for row in rows:
        worksheet.append(row)
    from io import BytesIO

    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    buffer.name = "padron.xlsx"
    return buffer


def crear_planilla_cuotas(rows):
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "COBRO CUOTAS SOCIALES"
    worksheet.append([None, None, None, None, None, "PAGO DE CUOTAS SOCIALES 2026"])
    worksheet.append([])
    worksheet.append([None, "ACTIVOS", None, "A/T: pago a término del 1 al 10 de cada mes"])
    worksheet.append([None, "ADHERENTES", None, "C/I: pago con interés después del 10"])
    worksheet.append([None, None, None, "AFT: asociado fuera de término (no se asoció en marzo)"])
    worksheet.append([])
    worksheet.append(
        [
            "Socio N°",
            "Apellido/Nombre",
            "curso/división",
            "Mar",
            "forma pago",
            "Abr",
            "forma pago",
            "May",
            "forma pago",
            "Jun",
            "froma pago",
        ]
    )
    for row in rows:
        worksheet.append(row)

    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    buffer.name = "cuotas.xlsx"
    return buffer


@pytest.mark.django_db
def test_dashboard_gestion_requiere_staff(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="aso_sin_staff", password="secreto123")
    client.force_login(user)

    response = client.get(reverse("gestion:dashboard"))

    assert response.status_code == 403


@pytest.mark.django_db
def test_dashboard_gestion_muestra_accesos_basicos(client):
    user_model = get_user_model()
    staff = user_model.objects.create_user(username="staff1", password="secreto123", is_staff=True)

    client.force_login(staff)
    response = client.get(reverse("gestion:dashboard"))

    assert response.status_code == 200
    content = response.content.decode()
    assert "Panel de gestión" in content
    assert "Asociados" in content
    assert "Cobros" in content
    assert "Deudores" in content
    assert "Períodos de cuota" in content
    assert "asociados activos" not in content.lower()


@pytest.mark.django_db
def test_cobros_gestion_requiere_staff(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="no_staff", password="secreto123")
    client.force_login(user)

    response = client.get(reverse("gestion:cobros"))

    assert response.status_code == 403


@pytest.mark.django_db
def test_deudores_gestion_requiere_staff(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="no_staff_deuda", password="secreto123")
    client.force_login(user)

    response = client.get(reverse("gestion:deudores"))

    assert response.status_code == 403


@pytest.mark.django_db
def test_periodos_cuota_gestion_requiere_staff(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="no_staff_periodos", password="secreto123")
    client.force_login(user)

    response = client.get(reverse("gestion:periodos_cuota"))

    assert response.status_code == 403


@pytest.mark.django_db
def test_asociados_gestion_requiere_staff(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="no_staff_asoc", password="secreto123")
    client.force_login(user)

    response = client.get(reverse("gestion:asociados"))

    assert response.status_code == 403


@pytest.mark.django_db
def test_exportar_asociados_requiere_staff(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="no_staff_exporta", password="secreto123")
    client.force_login(user)

    response = client.get(reverse("gestion:exportar_asociados"))

    assert response.status_code == 403


@pytest.mark.django_db
def test_importar_asociados_previsualiza_y_guarda_en_sesion(client):
    user_model = get_user_model()
    staff = user_model.objects.create_user(username="staff_importa", password="secreto123", is_staff=True)
    archivo = crear_planilla_padron(
        [
            [1, "Leyes Lena Muriel", "1°2°", "CB", "Activo", "52328996", "2984 111111", "lena@example.com", "Calle 1"],
            [2, "Joaquin Darosa", "1ro C.B", "CB", "Activo", "52536191", "2984 222222", "joaquin@example.com", "Calle 2"],
            [3, "", "", "", "", "", "", "", ""],
        ]
    )

    client.force_login(staff)
    response = client.post(
        reverse("gestion:importar_asociados"),
        {"action": "preview", "archivo": archivo},
        follow=True,
    )

    assert response.status_code == 200
    preview = client.session[PADRON_IMPORT_SESSION_KEY]
    assert preview["summary"]["importar"] == 1
    assert preview["summary"]["revisar"] == 1
    assert preview["summary"]["cursos_a_crear"] == 1
    assert preview["cursos_a_crear"][0]["curso"] == "1ro 2da CB TM"
    content = response.content.decode()
    assert "Cursos que se crearían" in content
    assert "Falta división/comisión del curso" in content
    assert "Cómo leer la previsualización" in content
    assert "Descargar planilla para revisar" in content


@pytest.mark.django_db
def test_importar_asociados_ordena_cursos_por_ciclo_anio_division_y_turno(client):
    user_model = get_user_model()
    staff = user_model.objects.create_user(username="staff_orden_cursos", password="secreto123", is_staff=True)
    archivo = crear_planilla_padron(
        [
            [1, "Perez Ana", "4°2°", "CS", "Activo", "42328996", "2984 111111", "ana@example.com", "Calle 1"],
            [2, "Lopez Beto", "1°2°", "CB", "Activo", "42536191", "2984 222222", "beto@example.com", "Calle 2"],
            [3, "Garcia Carla", "4°1°", "CS", "Activo", "43328996", "2984 333333", "carla@example.com", "Calle 3"],
            [4, "Sosa Diego", "1°1°", "CB", "Activo", "43536191", "2984 444444", "diego@example.com", "Calle 4"],
        ]
    )

    client.force_login(staff)
    response = client.post(reverse("gestion:importar_asociados"), {"action": "preview", "archivo": archivo})

    assert response.status_code == 302
    preview = client.session[PADRON_IMPORT_SESSION_KEY]
    assert [curso["curso"] for curso in preview["cursos_a_crear"]] == [
        "1ro 1ra CB TM",
        "1ro 2da CB TM",
        "4to 1ra CS TM",
        "4to 2da CS TM",
    ]


@pytest.mark.django_db
def test_importar_asociados_descarga_planilla_con_filas_a_revisar(client):
    user_model = get_user_model()
    staff = user_model.objects.create_user(username="staff_descarga_revisar", password="secreto123", is_staff=True)
    archivo = crear_planilla_padron(
        [
            [1, "Leyes Lena Muriel", "1°2°", "CB", "Activo", "52328996", "2984 111111", "lena@example.com", "Calle 1"],
            [2, "Joaquin Darosa", "1ro C.B", "CB", "Activo", "52536191", "2984 222222", "joaquin@example.com", "Calle 2"],
        ]
    )

    client.force_login(staff)
    client.post(reverse("gestion:importar_asociados"), {"action": "preview", "archivo": archivo})
    response = client.get(reverse("gestion:descargar_asociados_revisar"))

    assert response.status_code == 200
    assert response["Content-Type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert "padron_asociados_a_revisar.xlsx" in response["Content-Disposition"]

    workbook = load_workbook(BytesIO(response.content))
    worksheet = workbook["PADRÓN GENERAL"]
    assert [worksheet.cell(1, column).value for column in range(1, 12)] == [
        "Fila original",
        "Número de asociado",
        "Apellido/nombre",
        "Curso/división/Ciclo/turno",
        "CICLO",
        "Categoria (act./adh.)",
        "DNI",
        "Celular",
        "Mail",
        "Dirección",
        "Motivo de revisión",
    ]
    assert worksheet.max_row == 2
    row_values = [worksheet.cell(2, column).value for column in range(1, 12)]
    assert row_values[:10] == [
        3,
        "2",
        "Joaquin Darosa",
        "1ro C.B",
        "CB",
        "Activo",
        "52536191",
        "2984 222222",
        "joaquin@example.com",
        "Calle 2",
    ]
    assert "Falta división/comisión del curso" in row_values[10]
    assert "curso incompleto o dudoso para asociado" in row_values[10]


@pytest.mark.django_db
def test_importar_asociados_confirma_desde_sesion(client):
    user_model = get_user_model()
    staff = user_model.objects.create_user(username="staff_confirma", password="secreto123", is_staff=True)
    archivo = crear_planilla_padron(
        [
            [1, "Leyes Lena Muriel", "1°2°", "CB", "Activo", "52328996", "2984 111111", "lena@example.com", "Calle 1"],
            [2, "Joaquin Darosa", "1ro C.B", "CB", "Activo", "52536191", "2984 222222", "joaquin@example.com", "Calle 2"],
        ]
    )

    client.force_login(staff)
    client.post(reverse("gestion:importar_asociados"), {"action": "preview", "archivo": archivo})
    response = client.post(reverse("gestion:importar_asociados"), {"action": "confirm"}, follow=True)

    assert response.status_code == 200
    assert PADRON_IMPORT_SESSION_KEY not in client.session
    assert Curso.objects.filter(anio="1ro", curso="2da", division=Curso.DIVISION_CB, turno=Curso.TURNO_TM).exists()
    asociado = Asociado.objects.get(dni="52328996")
    assert asociado.apellido == "Leyes"
    assert asociado.nombre == "Lena Muriel"
    assert asociado.numero_asociado == 1
    assert asociado.direccion == "Calle 1"
    assert asociado.fecha_alta == timezone.localdate()
    assert not Asociado.objects.filter(dni="52536191").exists()
    assert "1 creados" in response.content.decode()


@pytest.mark.django_db
def test_importar_cuotas_historicas_previsualiza_desde_planilla(client):
    user_model = get_user_model()
    staff = user_model.objects.create_user(username="staff_cuotas_preview", password="secreto123", is_staff=True)
    asociado = create_asociado(
        nombre="Lena", apellido="Leyes", dni="52328996", tipo="asociado", fecha_alta="2026-03-01"
    )
    archivo = crear_planilla_cuotas(
        [
            [
                asociado.numero_asociado,
                "Leyes Lena Muriel",
                "1°2°",
                True,
                "efectivo",
                False,
                None,
                True,
                "MP",
                False,
                None,
            ],
            [999, "Persona Inexistente", "1°1°", True, "efectivo", False, None, False, None, False, None],
            [1000, None, "1°1°", True, "efectivo", False, None, False, None, False, None],
        ]
    )

    client.force_login(staff)
    response = client.post(
        reverse("gestion:importar_cuotas_historicas"),
        {"action": "preview", "archivo": archivo},
        follow=True,
    )

    assert response.status_code == 200
    preview = client.session["cuotas_historicas_preview"]
    assert preview["summary"]["cuotas_a_crear"] == 4
    assert preview["summary"]["pagos_a_crear"] == 2
    assert preview["summary"]["cuotas_impagas"] == 2
    assert preview["summary"]["revisar"] == 4
    assert preview["summary"]["omitidas"] == 1
    content = response.content.decode()
    assert "Cuotas importables" in content
    assert "No se encontró asociado por número" in content
    assert "No crea asientos contables" in content


@pytest.mark.django_db
def test_importar_cuotas_historicas_descarga_planilla_con_cuotas_a_revisar(client):
    user_model = get_user_model()
    staff = user_model.objects.create_user(username="staff_cuotas_revisar", password="secreto123", is_staff=True)
    archivo = crear_planilla_cuotas(
        [
            [999, "Persona Inexistente", "1°1°", True, "efectivo", False, None, False, "MP", False, None],
        ]
    )

    client.force_login(staff)
    client.post(reverse("gestion:importar_cuotas_historicas"), {"action": "preview", "archivo": archivo})
    response = client.get(reverse("gestion:descargar_cuotas_historicas_revisar"))

    assert response.status_code == 200
    assert response["Content-Type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert "cuotas_historicas_a_revisar.xlsx" in response["Content-Disposition"]

    workbook = load_workbook(BytesIO(response.content))
    worksheet = workbook["COBRO CUOTAS SOCIALES"]
    assert [worksheet.cell(1, column).value for column in range(1, 17)] == [
        "Fila original",
        "Número de asociado",
        "Apellido/Nombre",
        "curso/división",
        "Mar pago",
        "Mar forma",
        "Mar motivo",
        "Abr pago",
        "Abr forma",
        "Abr motivo",
        "May pago",
        "May forma",
        "May motivo",
        "Jun pago",
        "Jun forma",
        "Jun motivo",
    ]
    assert worksheet.max_row == 2
    row_values = [worksheet.cell(2, column).value for column in range(1, 17)]
    assert row_values[:6] == [8, 999, "Persona Inexistente", "1°1°", "Sí", "efectivo"]
    assert "No se encontró asociado por número" in row_values[6]
    assert row_values[10:12] == ["No", "MP"]
    assert "No se encontró asociado por número" in row_values[12]
    assert "Cuota impaga con forma de pago cargada" in row_values[12]


@pytest.mark.django_db
def test_importar_cuotas_historicas_confirma_sin_crear_asientos(client):
    user_model = get_user_model()
    staff = user_model.objects.create_user(username="staff_cuotas_confirma", password="secreto123", is_staff=True)
    asociado = create_asociado(
        nombre="Lena", apellido="Leyes", dni="52328996", tipo="asociado", fecha_alta="2026-03-01"
    )
    archivo = crear_planilla_cuotas(
        [
            [
                asociado.numero_asociado,
                "Leyes Lena Muriel",
                "1°2°",
                True,
                "efectivo",
                False,
                None,
                True,
                "MP",
                False,
                None,
            ],
        ]
    )

    client.force_login(staff)
    client.post(reverse("gestion:importar_cuotas_historicas"), {"action": "preview", "archivo": archivo})
    response = client.post(reverse("gestion:importar_cuotas_historicas"), {"action": "confirm"}, follow=True)

    assert response.status_code == 200
    assert PeriodoCuota.objects.filter(ciclo_lectivo__anio=2026, mes__in=[3, 4, 5, 6]).count() == 4
    assert Cuota.objects.filter(asociado=asociado).count() == 4
    assert Pago.objects.filter(asociado=asociado).count() == 2
    assert PagoCuota.objects.filter(pago__asociado=asociado).count() == 2
    assert Asiento.objects.count() == 0
    marzo = Cuota.objects.get(asociado=asociado, periodo__mes=3)
    abril = Cuota.objects.get(asociado=asociado, periodo__mes=4)
    assert marzo.estado == Cuota.ESTADO_PAGADA
    assert marzo.importe == 500
    assert marzo.importe_recargo_mora == 100
    assert abril.estado == Cuota.ESTADO_VENCIDA
    assert "4 cuotas creadas" in response.content.decode()


@pytest.mark.django_db
def test_cobros_gestion_busca_asociado_y_registra_pago(client):
    user_model = get_user_model()
    staff = user_model.objects.create_user(username="staff_cobro", password="secreto123", is_staff=True)
    asociado = create_asociado(
        nombre="Paula", apellido="Gimenez", dni="45555111", tipo="asociado", fecha_alta="2026-05-10"
    )
    crear_cuentas_contables_basicas()
    periodo = PeriodoCuota.objects.create(
        mes=timezone.localdate().month,
        ciclo_lectivo=CicloLectivo.objects.get_or_create(anio=timezone.localdate().year)[0],
        importe="3000.00",
        importe_recargo_mora="0.00",
        fecha_vencimiento=timezone.localdate(),
    )
    generar_cuotas_para_periodo(periodo)

    client.force_login(staff)

    response_busqueda = client.get(reverse("gestion:cobros"), {"q": "45555111"})
    assert response_busqueda.status_code == 200
    assert "Gimenez" in response_busqueda.content.decode()

    response_cobro = client.post(
        reverse("gestion:cobros"),
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
        nombre="Ivan", apellido="Molina", dni="46666111", tipo="asociado", fecha_alta="2026-05-10"
    )
    crear_cuentas_contables_basicas()
    periodo = PeriodoCuota.objects.create(
        mes=timezone.localdate().month,
        ciclo_lectivo=CicloLectivo.objects.get_or_create(anio=timezone.localdate().year)[0],
        importe="3000.00",
        importe_recargo_mora="0.00",
        fecha_vencimiento=timezone.localdate(),
    )
    generar_cuotas_para_periodo(periodo)

    client.force_login(staff)
    response = client.post(
        reverse("gestion:cobros"),
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
        nombre="Lucia", apellido="Ramos", dni="47777111", tipo="asociado", fecha_alta="2026-05-10"
    )
    crear_cuentas_contables_basicas()
    periodo = PeriodoCuota.objects.create(
        mes=timezone.localdate().month,
        ciclo_lectivo=CicloLectivo.objects.get_or_create(anio=timezone.localdate().year)[0],
        importe="3000.00",
        importe_recargo_mora="0.00",
        fecha_vencimiento=timezone.localdate(),
    )
    generar_cuotas_para_periodo(periodo)

    client.force_login(staff)
    response = client.get(reverse("gestion:deudores"))

    assert response.status_code == 200
    content = response.content.decode()
    assert "Ramos" in content
    assert f"?asociado={asociado.id}" in content


@pytest.mark.django_db
def test_periodos_cuota_gestion_crea_periodo(client):
    user_model = get_user_model()
    staff = user_model.objects.create_user(username="staff_periodo", password="secreto123", is_staff=True)
    client.force_login(staff)

    ciclo, _ = CicloLectivo.objects.get_or_create(anio=2026)
    response = client.post(
        reverse("gestion:periodos_cuota"),
        {
            "action": "crear_periodo",
            "mes": 6,
            "ciclo_lectivo": ciclo.id,
            "importe": "3200.00",
            "importe_recargo_mora": "500.00",
            "fecha_vencimiento": "2026-06-10",
            "activo": "on",
        },
        follow=True,
    )

    assert response.status_code == 200
    assert PeriodoCuota.objects.filter(mes=6, ciclo_lectivo__anio=2026, importe="3200.00").exists()
    assert "Periodo 06/2026 creado correctamente" in response.content.decode()


@pytest.mark.django_db
def test_periodos_cuota_gestion_genera_cuotas_sin_duplicar(client):
    user_model = get_user_model()
    staff = user_model.objects.create_user(username="staff_generacion", password="secreto123", is_staff=True)
    create_asociado(nombre="Lara", apellido="Suarez", dni="48888111", tipo="asociado", fecha_alta="2026-05-10")
    create_asociado(nombre="Nico", apellido="Ferreyra", dni="49999111", tipo="asociado", fecha_alta="2026-05-20")
    periodo = PeriodoCuota.objects.create(
        mes=6,
        ciclo_lectivo=CicloLectivo.objects.get_or_create(anio=2026)[0],
        importe="3200.00",
        importe_recargo_mora="500.00",
        fecha_vencimiento="2026-06-10",
    )

    client.force_login(staff)

    primer_response = client.post(
        reverse("gestion:periodos_cuota"),
        {"action": "generar_cuotas", "periodo_id": periodo.id},
        follow=True,
    )
    assert primer_response.status_code == 200
    assert periodo.cuotas.count() == 2
    assert "2 cuotas creadas" in primer_response.content.decode()

    segunda_response = client.post(
        reverse("gestion:periodos_cuota"),
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
        nombre="Julia", apellido="Campos", dni="40000111", tipo="asociado", fecha_alta="2026-05-10"
    )

    client.force_login(staff)
    listado = client.get(reverse("gestion:asociados"), {"q": "Campos"})

    assert listado.status_code == 200
    content = listado.content.decode()
    assert "Campos" in content
    assert reverse("gestion:exportar_asociados") in content
    assert "?q=Campos" in content

    detalle = client.get(reverse("gestion:asociado_detalle", args=[asociado.id]))

    assert detalle.status_code == 200
    content = detalle.content.decode()
    assert "Julia" in content
    assert "Sin usuario" in content
    assert f"?asociado={asociado.id}" in content


@pytest.mark.django_db
def test_exportar_asociados_descarga_formato_uni2_filtrado(client):
    user_model = get_user_model()
    staff = user_model.objects.create_user(username="staff_exporta", password="secreto123", is_staff=True)
    curso = Curso.objects.create(anio="1ro", curso="2da", division=Curso.DIVISION_CB, turno=Curso.TURNO_TM)
    create_asociado(
        nombre="Julia",
        apellido="Campos",
        dni="40000111",
        tipo="asociado",
        fecha_alta="2026-05-10",
        curso_actual=curso,
        email="julia@example.com",
        telefono="2984 123456",
        direccion="Calle 1",
    )
    create_asociado(
        nombre="Mora",
        apellido="Rivas",
        dni="40000222",
        tipo="adherente",
        fecha_alta="2026-05-11",
    )

    client.force_login(staff)
    response = client.get(reverse("gestion:exportar_asociados"), {"q": "Campos"})

    assert response.status_code == 200
    assert response["Content-Type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert "asociados_formato_uni2.xlsx" in response["Content-Disposition"]

    workbook = load_workbook(BytesIO(response.content))
    worksheet = workbook["ASOCIADOS"]
    assert [worksheet.cell(1, column).value for column in range(1, 18)] == [
        "numero_asociado",
        "apellido",
        "nombre",
        "dni",
        "tipo",
        "email",
        "telefono",
        "direccion",
        "curso_anio",
        "curso_division",
        "division",
        "turno",
        "curso_nombre",
        "fecha_alta",
        "fecha_inicio_cobro",
        "estado",
        "motivo_baja",
    ]
    assert worksheet.max_row == 2
    row_values = [worksheet.cell(2, column).value for column in range(1, 18)]
    assert row_values[1:17] == [
        "Campos",
        "Julia",
        "40000111",
        "asociado",
        "julia@example.com",
        "2984 123456",
        "Calle 1",
        "1ro",
        "2da",
        "CB",
        "TM",
        "1ro 2da CB TM",
        "2026-05-10",
        "2026-05-01",
        "activo",
        None,
    ]


@pytest.mark.django_db
def test_asociado_detalle_permite_editar_fecha_inicio_cobro(client):
    user_model = get_user_model()
    staff = user_model.objects.create_user(username="staff_edita_asoc", password="secreto123", is_staff=True)
    asociado = create_asociado(
        nombre="Milena", apellido="Armada", dni="30000111", tipo="asociado", fecha_alta="2026-05-22"
    )

    client.force_login(staff)
    response = client.post(
        reverse("gestion:asociado_detalle", args=[asociado.id]),
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
