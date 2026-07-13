import re
from pathlib import Path

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.staticfiles import finders
from django.urls import reverse

from comercios.models import ActividadComercial, Comercio
from contenidos.models import CategoriaProductoServicio, ProductoServicio, Publicidad


@pytest.mark.django_db
@pytest.mark.parametrize(
    "url_name",
    [
        "web:home",
        "web:productos_servicios",
        "web:comercios",
    ],
)
def test_paginas_publicas_responden(client, url_name):
    response = client.get(reverse(url_name))
    assert response.status_code == 200


def test_url_beneficios_no_se_mantiene(client):
    response = client.get("/beneficios/")

    assert response.status_code == 404


@pytest.mark.django_db
def test_design_system_requiere_login(client):
    response = client.get(reverse("web:design-system"))

    assert response.status_code == 302
    assert response.url == f'{reverse("usuarios:login")}?next={reverse("web:design-system")}'


@pytest.mark.django_db
def test_design_system_requiere_permiso(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="sin_design_system", password="secreto123")
    client.force_login(user)

    response = client.get(reverse("web:design-system"))

    assert response.status_code == 403


@pytest.mark.django_db
def test_design_system_con_permiso_responde(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="con_design_system", password="secreto123")
    permiso = Permission.objects.get(content_type__app_label="gestion", codename="ver_design_system")
    user.user_permissions.add(permiso)
    client.force_login(user)

    response = client.get(reverse("web:design-system"))

    assert response.status_code == 200
    assert "Sistema visual UNI2" in response.content.decode()


@pytest.mark.django_db
def test_design_system_porta_secciones_del_showcase(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="showcase_completo", password="secreto123")
    permiso = Permission.objects.get(content_type__app_label="gestion", codename="ver_design_system")
    user.user_permissions.add(permiso)
    client.force_login(user)

    response = client.get(reverse("web:design-system"))

    content = response.content.decode()
    assert response.status_code == 200
    assert "Sistema visual UNI2" in content
    assert "Servicios que suman" in content
    assert "Club de Beneficios" in content
    assert "Django" in content
    # La página usa el chrome del sitio (base.html): navbar, footer y tema
    assert "uni2-navbar" in content
    assert "uni2-theme.js" in content
    assert "style2.css" not in content
    assert "assets/logos/" not in content
    assert "benefit-list-body" in content
    assert "discount-tag" in content
    assert "uni2-metric" in content
    assert "uni2-status" in content
    assert "ds-metric" not in content
    assert "ds-status" not in content
    assert "uni2-service-grid" in content
    assert 'class="py-5 px-3 px-md-4 px-xl-5"' in content
    assert 'class="py-5 px-3 px-md-4 px-xl-5 bg-body-tertiary"' in content
    assert 'class="card-body"' in content
    assert 'class="service-grid"' not in content
    assert 'class="cta"' not in content
    clases_ds = set(re.findall(r"ds-[a-z0-9-]+", content))
    assert clases_ds == set(), f"clases ds-* inesperadas: {clases_ds}"


def test_css_design_system_acota_navegacion_y_no_conserva_aliases_huerfanos():
    css_path = finders.find("css/uni2-design-system.css")
    assert css_path is not None

    css = Path(css_path).read_text(encoding="utf-8")

    # Después de la limpieza arquitectural no debe quedar ningún selector ds-page
    assert "ds-page" not in css


@pytest.mark.django_db
def test_productos_servicios_publicos_muestran_activos_ordenados_y_cta_linkeable(client):
    categoria = CategoriaProductoServicio.objects.create(
        nombre="Impresiones",
        descripcion="Servicios para estudiantes",
        etiqueta_icono="printer",
        texto_cta="Consultá disponibilidad uni2mutual@gmail.com",
        activa=True,
        orden=1,
    )
    CategoriaProductoServicio.objects.create(
        nombre="Categoria inactiva",
        descripcion="No visible",
        activa=False,
        orden=2,
    )
    ProductoServicio.objects.create(
        categoria=categoria,
        nombre="Tercero",
        descripcion="Visible tercero",
        precio_asociados=600,
        precio_no_asociados=900,
        activo=True,
        orden=3,
    )
    ProductoServicio.objects.create(
        categoria=categoria,
        nombre="Inactivo",
        descripcion="No visible",
        precio_asociados=600,
        precio_no_asociados=900,
        activo=False,
        orden=1,
    )
    ProductoServicio.objects.create(
        categoria=categoria,
        nombre="Primero",
        descripcion="Visible primero",
        precio_asociados=400,
        precio_no_asociados=700,
        activo=True,
        orden=1,
    )
    ProductoServicio.objects.create(
        categoria=categoria,
        nombre="Segundo",
        descripcion="Visible segundo",
        es_servicio=True,
        precio_asociados=500,
        precio_no_asociados=800,
        activo=True,
        orden=2,
    )

    response = client.get(reverse("web:productos_servicios"))

    contenido = response.content.decode()
    assert contenido.index("Primero") < contenido.index("Segundo") < contenido.index("Tercero")
    assert "Inactivo" not in contenido
    assert "Categoria inactiva" not in contenido
    assert "Servicio" in contenido
    assert "$400,00" in contenido
    assert "mailto:uni2mutual@gmail.com" in contenido


@pytest.mark.django_db
def test_home_muestra_publicidades_activas_con_foto_y_links(client):
    categoria = CategoriaProductoServicio.objects.create(nombre="Impresiones", descripcion="Servicios")
    producto = ProductoServicio.objects.create(
        categoria=categoria,
        nombre="Anillado",
        descripcion="Anillado simple",
        precio_asociados=600,
        precio_no_asociados=900,
    )
    actividad = ActividadComercial.objects.create(nombre="Librería")
    comercio = Comercio.objects.create(
        nombre="Librería Sur",
        direccion="Mitre 123",
        actividad_comercial=actividad,
        beneficio_texto="10% en útiles",
        estado=Comercio.ESTADO_FIRMADO,
    )
    Publicidad.objects.create(
        titulo="Anillado destacado",
        descripcion="Apuntes listos para cursar.",
        etiqueta_principal="Servicio",
        etiqueta_secundaria="Nuevo",
        foto="publicidades/anillado.webp",
        producto_servicio=producto,
        activa=True,
        orden=1,
    )
    Publicidad.objects.create(
        titulo="Librería destacada",
        descripcion="Útiles escolares.",
        etiqueta_principal="Comercio",
        etiqueta_secundaria="10% OFF",
        foto="publicidades/libreria.webp",
        comercio=comercio,
        activa=True,
        orden=2,
    )
    Publicidad.objects.create(
        titulo="Oculta",
        descripcion="No visible.",
        etiqueta_principal="Promo",
        etiqueta_secundaria="OFF",
        foto="publicidades/oculta.webp",
        activa=False,
        orden=3,
    )

    response = client.get(reverse("web:home"))

    contenido = response.content.decode()
    assert "Nuestros favoritos" in contenido
    assert contenido.index("Anillado destacado") < contenido.index("Librería destacada")
    assert "Oculta" not in contenido
    assert "publicidades/anillado.webp" in contenido
    assert reverse("web:producto_servicio_detalle", args=[producto.id]) in contenido
    assert reverse("web:comercio_detalle", args=[comercio.id]) in contenido


@pytest.mark.django_db
def test_home_muestra_publicidad_sin_foto_sin_error(client):
    Publicidad.objects.create(
        titulo="Bicicleta solidaria",
        descripcion="Préstamo gratuito de bicicletas.",
        etiqueta_principal="Programa",
        etiqueta_secundaria="Gratuito",
        activa=True,
        orden=1,
    )

    response = client.get(reverse("web:home"))

    contenido = response.content.decode()
    assert response.status_code == 200
    assert "Bicicleta solidaria" in contenido
    assert "Préstamo gratuito de bicicletas." in contenido
    assert "Conocer más" not in contenido


@pytest.mark.django_db
def test_home_usa_el_mismo_formato_visual_que_el_design_system(client):
    categoria = CategoriaProductoServicio.objects.create(nombre="Impresiones", descripcion="Servicios")
    ProductoServicio.objects.create(
        categoria=categoria,
        nombre="Anillado",
        descripcion="Anillado simple",
        precio_asociados=600,
        precio_no_asociados=900,
    )
    actividad = ActividadComercial.objects.create(nombre="Librería")
    Comercio.objects.create(
        nombre="Librería Sur",
        direccion="Mitre 123",
        actividad_comercial=actividad,
        beneficio_texto="10% en útiles",
        estado=Comercio.ESTADO_FIRMADO,
        foto=SimpleUploadedFile("libreria.jpg", b"content", content_type="image/jpeg"),
    )

    response = client.get(reverse("web:home"))

    content = response.content.decode()
    assert response.status_code == 200
    assert "uni2-service-grid" in content
    assert "uni2-section-heading" in content
    assert "uni2-benefit-band" in content
    assert "uni2-benefit-mix-card" in content
    assert "uni2-benefit-links" in content
    assert 'class="benefit-band"' not in content
    assert "uni2-hours-mobile" in content
    assert 'class="service-grid"' not in content


@pytest.mark.django_db
def test_home_muestra_horarios_en_formato_movil_compacto(client):
    response = client.get(reverse("web:home"))

    content = response.content.decode()
    assert response.status_code == 200
    assert "uni2-hours-mobile" in content
    assert "uni2-hours-day" in content
    assert "uni2-hours-chip-blue" in content
    assert "uni2-hours-chip-muted" in content


@pytest.mark.django_db
def test_home_muestra_beneficios_con_fotos_de_cada_rubro(client):
    foto_1 = SimpleUploadedFile("gastronomia-1.jpg", b"content", content_type="image/jpeg")
    foto_2 = SimpleUploadedFile("gastronomia-2.jpg", b"content", content_type="image/jpeg")
    foto_3 = SimpleUploadedFile("gastronomia-3.jpg", b"content", content_type="image/jpeg")
    foto_4 = SimpleUploadedFile("libreria-1.jpg", b"content", content_type="image/jpeg")
    foto_5 = SimpleUploadedFile("libreria-2.jpg", b"content", content_type="image/jpeg")
    foto_6 = SimpleUploadedFile("libreria-3.jpg", b"content", content_type="image/jpeg")

    gastronomia = ActividadComercial.objects.create(nombre="Gastronomía")
    libreria = ActividadComercial.objects.create(nombre="Librería")

    for orden, foto in enumerate([foto_1, foto_2, foto_3], start=1):
        Comercio.objects.create(
            nombre=f"Gastronomía {orden}",
            actividad_comercial=gastronomia,
            beneficio_texto="10% off",
            estado=Comercio.ESTADO_FIRMADO,
            orden=orden,
            direccion=f"Calle {orden}",
            foto=foto,
        )

    for orden, foto in enumerate([foto_4, foto_5, foto_6], start=1):
        Comercio.objects.create(
            nombre=f"Librería {orden}",
            actividad_comercial=libreria,
            beneficio_texto="15% off",
            estado=Comercio.ESTADO_FIRMADO,
            orden=orden,
            direccion=f"Avenida {orden}",
            foto=foto,
        )

    response = client.get(reverse("web:home"))

    contenido = response.content.decode()
    assert response.status_code == 200
    assert "Gastronomía" in contenido
    assert "Librería" in contenido
    assert 'alt="Gastronomía 1"' in contenido
    assert 'alt="Librería 1"' in contenido


@pytest.mark.django_db
def test_home_muestra_logo_unico_por_posicion_en_beneficios(client):
    foto = SimpleUploadedFile("gastronomia-unica.jpg", b"content", content_type="image/jpeg")
    rubro = ActividadComercial.objects.create(nombre="Gastronomía")
    Comercio.objects.create(
        nombre="Gastronomía Central",
        actividad_comercial=rubro,
        beneficio_texto="10% off",
        estado=Comercio.ESTADO_FIRMADO,
        orden=1,
        direccion="Calle 1",
        foto=foto,
    )

    response = client.get(reverse("web:home"))

    contenido = response.content.decode()
    assert response.status_code == 200
    assert "uni2-benefit-logo-dot-left" in contenido


@pytest.mark.django_db
def test_detalle_producto_servicio_publico_muestra_producto_activo(client):
    categoria = CategoriaProductoServicio.objects.create(nombre="Impresiones", descripcion="Servicios")
    producto = ProductoServicio.objects.create(
        categoria=categoria,
        nombre="Anillado",
        descripcion="Anillado simple",
        precio_asociados=600,
        precio_no_asociados=900,
        activo=True,
    )

    response = client.get(reverse("web:producto_servicio_detalle", args=[producto.id]))

    contenido = response.content.decode()
    assert response.status_code == 200
    assert "Anillado" in contenido
    assert "$600,00" in contenido


@pytest.mark.django_db
def test_detalle_comercio_publico_muestra_solo_comercio_firmado(client):
    actividad = ActividadComercial.objects.create(nombre="Librería")
    comercio = Comercio.objects.create(
        nombre="Librería Sur",
        direccion="Mitre 123",
        actividad_comercial=actividad,
        beneficio_texto="10% en útiles",
        estado=Comercio.ESTADO_FIRMADO,
    )
    pendiente = Comercio.objects.create(
        nombre="Librería Pendiente",
        direccion="Roca 100",
        actividad_comercial=actividad,
        beneficio_texto="No publicado",
        estado=Comercio.ESTADO_PENDIENTE,
    )

    response = client.get(reverse("web:comercio_detalle", args=[comercio.id]))
    response_pendiente = client.get(reverse("web:comercio_detalle", args=[pendiente.id]))

    contenido = response.content.decode()
    assert response.status_code == 200
    assert "Librería Sur" in contenido
    assert "10% en útiles" in contenido
    assert "Todos los comercios" not in contenido
    assert "Mitre 123" in contenido
    assert "commerce-benefit-logo" in contenido
    assert "Visitar online" not in contenido
    assert "Visitar sitio" not in contenido
    assert response_pendiente.status_code == 200
    assert "próximamente" in response_pendiente.content.decode()


@pytest.mark.django_db
def test_comercios_publicos_muestran_actividad_comercial(client):
    actividad = ActividadComercial.objects.create(nombre="Librería")
    Comercio.objects.create(
        nombre="Librería Zeta",
        direccion="Mitre 123",
        actividad_comercial=actividad,
        beneficio_texto="10% en útiles",
        estado=Comercio.ESTADO_FIRMADO,
        orden=1,
    )
    Comercio.objects.create(
        nombre="Librería Alfa",
        direccion="San Martín 55",
        actividad_comercial=actividad,
        beneficio_texto="2x1 en anillados",
        estado=Comercio.ESTADO_FIRMADO,
        orden=2,
    )
    Comercio.objects.create(
        nombre="Librería Pendiente",
        direccion="Roca 100",
        actividad_comercial=actividad,
        beneficio_texto="No publicado",
        estado=Comercio.ESTADO_PENDIENTE,
    )

    response = client.get(reverse("web:comercios"))

    contenido = response.content.decode()
    assert contenido.index("Librería Zeta") < contenido.index("Librería Alfa")
    assert "Actividad:" in contenido
    assert "Librería" in contenido
    assert "Presencia web" not in contenido
    assert "Visitar online" not in contenido
    assert "Librería Pendiente" not in contenido


def test_comercio_tiene_orden_para_publicacion():
    campo = Comercio._meta.get_field("orden")

    assert campo.verbose_name == "orden"


@pytest.mark.django_db
def test_categoria_detalle_muestra_sus_productos_activos(client):
    categoria = CategoriaProductoServicio.objects.create(
        nombre="Fotocopias",
        descripcion="Servicios de impresión",
        etiqueta_icono="printer",
        texto_cta="Consultá en la mutual",
        activa=True,
        orden=1,
    )
    ProductoServicio.objects.create(
        categoria=categoria,
        nombre="Fotocopia simple",
        descripcion="ByN",
        precio_asociados=50,
        precio_no_asociados=80,
        activo=True,
        orden=1,
    )
    ProductoServicio.objects.create(
        categoria=categoria,
        nombre="Inactivo",
        descripcion="No visible",
        precio_asociados=100,
        precio_no_asociados=150,
        activo=False,
        orden=2,
    )

    url = reverse("web:categoria_detalle", args=[categoria.pk])
    response = client.get(url)

    assert response.status_code == 200
    assert response.template_name == ["web/categoria_detalle.html"]
    contenido = response.content.decode()
    assert "Fotocopias" in contenido
    assert "Fotocopia simple" in contenido
    assert "Inactivo" not in contenido
    assert "$50,00" in contenido
    assert "Consultá en la mutual" in contenido


@pytest.mark.django_db
def test_categoria_detalle_404_si_inactiva_o_inexistente(client):
    categoria = CategoriaProductoServicio.objects.create(
        nombre="Oculta",
        descripcion="No visible",
        activa=False,
    )

    response = client.get(reverse("web:categoria_detalle", args=[categoria.pk]))
    assert response.status_code == 404

    response = client.get(reverse("web:categoria_detalle", args=[999]))
    assert response.status_code == 404


@pytest.mark.django_db
def test_actividad_comercial_detalle_muestra_sus_comercios_firmados(client):
    actividad = ActividadComercial.objects.create(nombre="Gastronomía")
    parrilla = Comercio.objects.create(
        nombre="Parrilla Don Pancho",
        direccion="Mitre 100",
        actividad_comercial=actividad,
        beneficio_texto="10% de descuento",
        estado=Comercio.ESTADO_FIRMADO,
        orden=1,
        foto=SimpleUploadedFile("parrilla.jpg", b"content", content_type="image/jpeg"),
    )
    Comercio.objects.create(
        nombre="Lo de Carlitos",
        direccion="Belgrano 200",
        actividad_comercial=actividad,
        beneficio_texto="2x1 en milanesas",
        estado=Comercio.ESTADO_FIRMADO,
        orden=2,
    )
    Comercio.objects.create(
        nombre="No Visible",
        direccion="Oculta 300",
        actividad_comercial=actividad,
        beneficio_texto="No publicado",
        estado=Comercio.ESTADO_PENDIENTE,
        orden=3,
    )

    url = reverse("web:actividad_comercial_detalle", args=[actividad.pk])
    response = client.get(url)

    assert response.status_code == 200
    assert response.template_name == ["web/actividadcomercial_detalle.html"]
    assert response.context["actividad_comercial"].nombre == "Gastronomía"
    contenido = response.content.decode()
    assert "Gastronomía" in contenido
    assert '<section class="benefit-page"' not in contenido
    assert contenido.count("benefit-list-card") == 2
    assert contenido.count("benefit-list-logo") >= 2
    assert "benefit-list-body" in contenido
    assert "benefit-meta" in contenido
    assert "discount-tag" in contenido
    assert "benefit-back" not in contenido
    assert "Actividad comercial" not in contenido
    assert "breadcrumb-item" not in contenido
    assert "Parrilla Don Pancho" in contenido
    assert "10% de descuento" in contenido
    assert "Lo de Carlitos" in contenido
    assert reverse("web:comercio_detalle", args=[parrilla.pk]) in contenido
    assert "No Visible" not in contenido


@pytest.mark.django_db
def test_actividad_comercial_detalle_404_sin_comercios_o_inexistente(client):
    actividad = ActividadComercial.objects.create(nombre="Vacía")

    response = client.get(reverse("web:actividad_comercial_detalle", args=[actividad.pk]))
    assert response.status_code == 404

    response = client.get(reverse("web:actividad_comercial_detalle", args=[999]))
    assert response.status_code == 404
