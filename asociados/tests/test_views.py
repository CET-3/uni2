from decimal import Decimal
from datetime import date

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from asociados.models import Asociado, CicloLectivo
from asociados.services import create_asociado
from comercios.models import ActividadComercial, Comercio
from contenidos.models import CategoriaProductoServicio, ProductoServicio, Publicidad
from cuotas.models import Cuota, PeriodoCuota


def crear_cuota_impaga(asociado, *, anio=2026, mes=7):
    ciclo, _ = CicloLectivo.objects.get_or_create(anio=anio)
    periodo = PeriodoCuota.objects.create(
        mes=mes,
        ciclo_lectivo=ciclo,
        importe="1000.00",
        importe_recargo_mes="0.00",
        importe_recargo_mes_siguiente="0.00",
        fecha_vencimiento=date(anio, mes, 10),
    )
    return Cuota.objects.create(asociado=asociado, periodo=periodo, importe="1000.00")


@pytest.mark.django_db
def test_ruta_anterior_del_panel_asociado_fue_retirada(client):
    response = client.get("/asociado/panel/")
    assert response.status_code == 404


@pytest.mark.django_db
def test_home_asociado_responde_con_usuario_vinculado(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="aso2", password="secreto123")
    asociado = create_asociado(
        nombre="Nora",
        apellido="Diaz",
        dni="40222999",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta=date(2026, 5, 10),
    )
    asociado.usuario = user
    asociado.save(update_fields=["usuario"])

    client.force_login(user)
    response = client.get(reverse("web:home"))

    assert response.status_code == 200
    assert "Nora" in response.content.decode()


@pytest.mark.django_db
def test_home_asociado_incluye_secciones_publicas(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="aso3", password="secreto123")
    asociado = create_asociado(
        nombre="Leo",
        apellido="Messi",
        dni="40223000",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta=date(2026, 5, 10),
    )
    asociado.usuario = user
    asociado.save(update_fields=["usuario"])

    categoria = CategoriaProductoServicio.objects.create(nombre="Impresiones", etiqueta_icono="printer")
    ProductoServicio.objects.create(
        categoria=categoria,
        nombre="Fotocopias",
        descripcion="Fotocopias rápidas y de excelente calidad.",
        precio_asociados=Decimal("10.00"),
        precio_no_asociados=Decimal("20.00"),
    )

    rubro = ActividadComercial.objects.create(nombre="Librerías")
    comercio = Comercio.objects.create(
        nombre="Librería Centro",
        actividad_comercial=rubro,
        estado=Comercio.ESTADO_FIRMADO,
    )
    Publicidad.objects.create(
        titulo="20% OFF",
        descripcion="Descuento exclusivo",
        etiqueta_principal="Imperdible",
        etiqueta_secundaria="En librería",
        activa=True,
    )

    client.force_login(user)
    response = client.get(reverse("web:home"))
    content = response.content.decode()

    assert response.status_code == 200
    assert "Servicios que suman" in content
    assert "Librerías" in content
    assert "20% OFF" in content


@pytest.mark.django_db
def test_credencial_propia_con_deuda_solo_muestra_el_estado_inactivo(client, monkeypatch):
    monkeypatch.setattr("asociados.views.timezone.localdate", lambda: date(2026, 8, 20))
    asociado = create_asociado(
        nombre="Nora",
        apellido="Deudora",
        dni="40999444",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta=date(2026, 6, 1),
    )
    crear_cuota_impaga(asociado)
    client.force_login(asociado.usuario)

    content = client.get(reverse("asociados:credencial")).content.decode()

    assert "Credencial inactiva" in content
    assert content.count("Credencial inactiva") == 1
    assert "cuotas pendientes" not in content
    assert "Revisar Mis cuotas" not in content
    assert 'data-credential-estado="Inactiva"' in content
    assert "data-credential-deuda" not in content


@pytest.mark.django_db
def test_credencial_propia_al_dia_se_muestra_activa_sin_explicacion_de_deuda(client):
    asociado = create_asociado(
        nombre="Nora",
        apellido="Al Día",
        dni="40999555",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta=date(2026, 6, 1),
    )
    client.force_login(asociado.usuario)

    content = client.get(reverse("asociados:credencial")).content.decode()

    assert "Credencial activa" in content
    assert 'data-credential-estado="Activa"' in content
    assert "cuotas pendientes" not in content


@pytest.mark.django_db
def test_credencial_agrupa_identidad_validacion_y_respaldo_sin_cabecera_visual(client):
    asociado = create_asociado(
        nombre="Nora",
        apellido="Diseño",
        dni="40999777",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta=date(2026, 6, 1),
    )
    client.force_login(asociado.usuario)

    content = client.get(reverse("asociados:credencial")).content.decode()

    assert 'aria-label="Credencial digital de Nora Diseño"' in content
    assert 'class="uni2-credential-brand"' in content
    assert 'class="uni2-credential-page-heading"' not in content
    assert ">Mi credencial</h1>" not in content
    assert "Presentala en los comercios para acceder a tus beneficios." not in content
    assert "<summary>Ver código de respaldo</summary>" in content
    assert content.index("uni2-credential-state") < content.index("uni2-credential-technical")


@pytest.mark.django_db
def test_credencial_propia_dada_de_baja_solo_muestra_el_estado_inactivo(client):
    asociado = create_asociado(
        nombre="Nora",
        apellido="Baja",
        dni="40999666",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta=date(2026, 6, 1),
    )
    asociado.estado = Asociado.ESTADO_INACTIVO
    asociado.save(update_fields=["estado"])
    client.force_login(asociado.usuario)

    content = client.get(reverse("asociados:credencial")).content.decode()

    assert "Credencial inactiva" in content
    assert content.count("Credencial inactiva") == 1
    assert "consultá a la mutual" not in content
    assert "cuotas pendientes" not in content
    assert 'data-credential-estado="Inactiva"' in content


@pytest.mark.django_db
@pytest.mark.parametrize("url_name", ["asociados:credencial", "asociados:cuotas"])
def test_pantallas_asociado_usan_contenedor_sin_familias_paralelas(client, url_name):
    asociado = create_asociado(
        nombre="Nora",
        apellido="Diseño",
        dni="40999111",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta=date(2026, 8, 1),
    )
    client.force_login(asociado.usuario)

    content = client.get(reverse(url_name)).content.decode()

    assert 'class="container py-5' in content
    assert "uni2-member-" not in content
    assert "uni2-ops-" not in content


@pytest.mark.django_db
def test_cuotas_asociado_usan_metricas_y_superficie_compartidas(client):
    asociado = create_asociado(
        nombre="Leo",
        apellido="Cuotas",
        dni="40999222",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta=date(2026, 8, 1),
    )
    client.force_login(asociado.usuario)

    content = client.get(reverse("asociados:cuotas")).content.decode()

    assert "uni2-metric-card" in content
    assert "uni2-surface-card" in content
    assert "Cuotas generadas" in content
    assert "Cuotas con deuda" in content


@pytest.mark.django_db
def test_cuotas_asociado_muestran_un_badge_semantico_por_estado(client, monkeypatch):
    fecha_referencia = date(2026, 8, 20)
    monkeypatch.setattr("asociados.views.timezone.localdate", lambda: fecha_referencia)
    asociado = create_asociado(
        nombre="Leo",
        apellido="Estados",
        dni="40999333",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta=date(2026, 6, 1),
    )
    ciclo = CicloLectivo.objects.create(anio=2026)
    periodo_pagado = PeriodoCuota.objects.create(
        mes=6,
        ciclo_lectivo=ciclo,
        importe="1000.00",
        fecha_vencimiento=date(2026, 6, 10),
    )
    periodo_vencido = PeriodoCuota.objects.create(
        mes=7,
        ciclo_lectivo=ciclo,
        importe="1000.00",
        fecha_vencimiento=date(2026, 7, 10),
    )
    periodo_pendiente = PeriodoCuota.objects.create(
        mes=8,
        ciclo_lectivo=ciclo,
        importe="1000.00",
        fecha_vencimiento=date(2026, 8, 31),
    )
    Cuota.objects.create(
        asociado=asociado,
        periodo=periodo_pagado,
        importe="1000.00",
        importe_pagado="1000.00",
    )
    Cuota.objects.create(asociado=asociado, periodo=periodo_vencido, importe="1000.00")
    Cuota.objects.create(asociado=asociado, periodo=periodo_pendiente, importe="1000.00")
    client.force_login(asociado.usuario)

    content = client.get(reverse("asociados:cuotas")).content.decode()
    table_start = content.index('<table class="table table-soft')
    table_end = content.index("</table>", table_start)
    table_content = content[table_start:table_end]

    assert "uni2-records-table-wrap" in content
    assert "uni2-records-table uni2-cuotas-table" in table_content
    assert table_content.count('class="uni2-records-table-row uni2-cuota-record"') == 3
    assert 'data-label="Importe"' in table_content
    assert 'data-label="Pagado"' in table_content
    assert 'data-label="Saldo"' in table_content
    assert 'data-label="Estado"' in table_content
    assert 'uni2-badge-success">Pagada</span>' in table_content
    assert 'uni2-badge-warning">Pendiente</span>' in table_content
    assert 'uni2-badge-danger">Vencida</span>' in table_content
    assert "uni2-badge-info" not in table_content
    assert table_content.count('class="uni2-badge ') == 3
    assert '<th class="text-end">Pagado</th>' in table_content
    assert '<th class="text-end">Saldo</th>' in table_content
    assert table_content.count('<td class="text-end" data-label=') == 6
