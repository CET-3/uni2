import json
import re
from xml.etree import ElementTree

import pytest
from django.test import override_settings
from django.urls import reverse

from comercios.models import ActividadComercial, Comercio
from contenidos.models import CategoriaProductoServicio, ProductoServicio


def structured_data(response):
    match = re.search(
        r'<script type="application/ld\+json">(.*?)</script>',
        response.content.decode(),
        re.DOTALL,
    )
    return json.loads(match.group(1)) if match else None


@pytest.mark.django_db
def test_home_declara_sitio_y_mutual_con_datos_publicos(client):
    data = structured_data(client.get("/"))
    assert data["@context"] == "https://schema.org"
    website, organization = data["@graph"]
    assert website == {"@type": "WebSite", "name": "UNI2", "url": "http://testserver/"}
    assert organization["@type"] == "Organization"
    assert organization["name"] == "Mutual Escolar UNI2"
    assert organization["url"] == "http://testserver/"
    assert organization["logo"] == "http://testserver/static/pwa/icons/icon-512.png"
    assert organization["address"]["streetAddress"] == "Chacabuco 1050"
    assert organization["sameAs"] == ["https://www.instagram.com/unidos.cet3"]


@pytest.mark.django_db
def test_fichas_declaran_breadcrumbs_iguales_a_la_navegacion_visible(client):
    categoria = CategoriaProductoServicio.objects.create(nombre="Fotocopias")
    producto = ProductoServicio.objects.create(categoria=categoria, nombre="Cuadernillo")
    actividad = ActividadComercial.objects.create(nombre="Librería")
    comercio = Comercio.objects.create(
        actividad_comercial=actividad, nombre="Librería Uno", descripcion="Libros",
        beneficio_texto="10 %", estado=Comercio.ESTADO_FIRMADO,
    )
    casos = (
        (categoria, [("Productos y servicios", "http://testserver/#productos-servicios"), ("Fotocopias", f"http://testserver{categoria.get_absolute_url()}")]),
        (producto, [("Productos y servicios", "http://testserver/#productos-servicios"), ("Fotocopias", f"http://testserver{categoria.get_absolute_url()}"), ("Cuadernillo", f"http://testserver{producto.get_absolute_url()}")]),
        (actividad, [("Comercios", "http://testserver/#beneficios"), ("Librería", f"http://testserver{actividad.get_absolute_url()}")]),
        (comercio, [("Comercios", "http://testserver/#beneficios"), ("Librería", f"http://testserver{actividad.get_absolute_url()}"), ("Librería Uno", f"http://testserver{comercio.get_absolute_url()}")]),
    )
    for obj, expected in casos:
        data = structured_data(client.get(obj.get_absolute_url()))
        assert data["@type"] == "BreadcrumbList"
        assert [(item["name"], item["item"]) for item in data["itemListElement"]] == expected
        assert [item["position"] for item in data["itemListElement"]] == list(range(1, len(expected) + 1))


@pytest.mark.django_db
def test_datos_estructurados_escapan_nombre_y_omiten_comercio_no_firmado(client):
    categoria = CategoriaProductoServicio.objects.create(nombre="Cuadernos </script>")
    response = client.get(categoria.get_absolute_url())
    assert structured_data(response)["itemListElement"][-1]["name"] == categoria.nombre
    assert "\\u003C/script\\u003E" in response.content.decode()

    actividad = ActividadComercial.objects.create(nombre="Librería")
    pendiente = Comercio.objects.create(
        actividad_comercial=actividad, nombre="Pendiente", descripcion="Próximamente",
        beneficio_texto="10 %", estado=Comercio.ESTADO_PENDIENTE,
    )
    assert structured_data(client.get(pendiente.get_absolute_url())) is None


@pytest.mark.django_db
def test_fichas_tienen_url_legible_y_redirigen_desde_la_anterior(client):
    categoria = CategoriaProductoServicio.objects.create(nombre="Fotocopias e impresiones")
    producto = ProductoServicio.objects.create(categoria=categoria, nombre="Cuadernillo de 1.º")
    actividad = ActividadComercial.objects.create(nombre="Gastronomía")
    comercio = Comercio.objects.create(
        actividad_comercial=actividad,
        nombre="Café del CET 3",
        descripcion="Cafetería escolar",
        beneficio_texto="10 %",
        estado=Comercio.ESTADO_FIRMADO,
    )
    casos = (
        ("categoria_detalle", categoria, "fotocopias-e-impresiones", "servicios"),
        ("producto_servicio_detalle", producto, "cuadernillo-de-1o", "productos-servicios"),
        ("actividad_comercial_detalle", actividad, "gastronomia", "actividades-comerciales"),
        ("comercio_detalle", comercio, "cafe-del-cet-3", "comercios"),
    )
    for nombre_ruta, objeto, slug, prefijo in casos:
        url = f"/{prefijo}/{objeto.pk}/{slug}/"
        assert objeto.get_absolute_url() == url
        assert client.get(reverse(f"web:{nombre_ruta}", args=[objeto.pk])).status_code == 301
        assert client.get(reverse(f"web:{nombre_ruta}", args=[objeto.pk]))["Location"] == url
        response = client.get(url)
        assert response.status_code == 200
        assert f"<title>{objeto.nombre} | UNI2</title>" in response.content.decode()
        assert f'<link rel="canonical" href="http://testserver{url}">' in response.content.decode()
        assert client.get(f"/{prefijo}/{objeto.pk}/nombre-viejo/")["Location"] == url


@pytest.mark.django_db
def test_sitemap_solo_publica_fichas_vigentes(client):
    categoria = CategoriaProductoServicio.objects.create(nombre="Fotocopias")
    producto = ProductoServicio.objects.create(categoria=categoria, nombre="Cuadernillo")
    oculta = CategoriaProductoServicio.objects.create(nombre="Oculta", activa=False)
    ProductoServicio.objects.create(categoria=oculta, nombre="Privado")
    actividad = ActividadComercial.objects.create(nombre="Librería")
    comercio = Comercio.objects.create(
        actividad_comercial=actividad, nombre="Librería Uno", descripcion="Libros",
        beneficio_texto="10 %", estado=Comercio.ESTADO_FIRMADO,
    )
    Comercio.objects.create(
        actividad_comercial=actividad, nombre="Pendiente", descripcion="No publicado",
        beneficio_texto="10 %", estado=Comercio.ESTADO_PENDIENTE,
    )
    response = client.get("/sitemap.xml")
    contenido = response.content.decode()
    assert response.status_code == 200
    assert response["Content-Type"].startswith("application/xml")
    ubicaciones = {
        element.text for element in ElementTree.fromstring(contenido).iter()
        if element.tag.endswith("loc")
    }
    assert ubicaciones == {
        f"http://testserver{url}" for url in (
            "/", "/productos-servicios/", "/comercios/", categoria.get_absolute_url(),
            producto.get_absolute_url(), actividad.get_absolute_url(), comercio.get_absolute_url(),
        )
    }


def test_robots_txt_indica_sitemap(client):
    respuesta = client.get("/robots.txt")
    assert respuesta.status_code == 200
    assert respuesta["Content-Type"].startswith("text/plain")
    assert respuesta.content.decode() == "User-agent: *\nSitemap: http://testserver/sitemap.xml\n"


@pytest.mark.django_db
def test_home_publica_presenta_mutual_y_metadatos(client):
    contenido = client.get("/").content.decode()
    assert '<h1 id="hero-title" class="uni2-titulo-principal">Tu mutual, más cerca que nunca</h1>' in contenido
    assert "<title>UNI2 | Mutual Escolar</title>" in contenido
    assert 'name="description" content="Conocé los servicios y beneficios de UNI2, la mutual escolar del CET 3 de General Roca."' in contenido
    assert '<link rel="canonical" href="http://testserver/">' in contenido
    assert '<meta property="og:title" content="UNI2 | Mutual Escolar">' in contenido
    assert '<meta property="og:description" content="Conocé los servicios y beneficios de UNI2, la mutual escolar del CET 3 de General Roca.">' in contenido
    assert '<meta property="og:url" content="http://testserver/">' in contenido
    assert '<meta property="og:image" content="http://testserver/static/pwa/icons/icon-512.png">' in contenido


@pytest.mark.django_db
def test_listados_publicos_tienen_titulos_y_descripciones_aprobados(client):
    casos = (
        (
            "/productos-servicios/",
            "Productos y servicios | UNI2",
            "Explorá los productos y servicios de UNI2, la mutual escolar del CET 3 de General Roca.",
        ),
        (
            "/comercios/",
            "Comercios adheridos | UNI2",
            "Descubrí los comercios adheridos y sus beneficios para asociados de UNI2, la mutual escolar del CET 3 de General Roca.",
        ),
    )
    for url, titulo, descripcion in casos:
        contenido = client.get(url).content.decode()
        assert f"<title>{titulo}</title>" in contenido
        assert f'name="description" content="{descripcion}"' in contenido


@pytest.mark.django_db
def test_listado_de_comercios_tiene_encabezado_principal(client):
    contenido = client.get("/comercios/").content.decode()
    assert '<h1 class="uni2-titulo-seccion">Comercios adheridos</h1>' in contenido


@pytest.mark.django_db
def test_nombre_modificado_y_repetido_mantiene_url_unica(client):
    primera = CategoriaProductoServicio.objects.create(nombre="Uniformes")
    segunda = ProductoServicio.objects.create(categoria=primera, nombre="Uniformes")
    anterior = primera.get_absolute_url()
    primera.nombre = "Uniformes escolares"
    primera.save(update_fields=["nombre"])

    assert primera.get_absolute_url() != anterior
    assert segunda.get_absolute_url() != primera.get_absolute_url()
    assert client.get(anterior)["Location"] == primera.get_absolute_url()


@pytest.mark.django_db
def test_comercio_no_firmado_no_se_indexa(client):
    actividad = ActividadComercial.objects.create(nombre="Librería")
    pendiente = Comercio.objects.create(
        actividad_comercial=actividad, nombre="Pendiente", descripcion="Aún no disponible",
        beneficio_texto="10 %", estado=Comercio.ESTADO_PENDIENTE,
    )
    response = client.get(pendiente.get_absolute_url())
    assert response.status_code == 200
    assert response["X-Robots-Tag"] == "noindex, nofollow"
    assert pendiente.get_absolute_url() not in client.get("/sitemap.xml").content.decode()


@pytest.mark.django_db
def test_ficha_sin_descripcion_tiene_resumen_con_nombre(client):
    categoria = CategoriaProductoServicio.objects.create(nombre="Bicicleta solidaria")
    contenido = client.get(categoria.get_absolute_url()).content.decode()
    assert 'name="description" content="Bicicleta solidaria. Una propuesta de la Mutual Escolar UNI2 del CET 3 de General Roca."' in contenido


@pytest.mark.django_db
def test_descripciones_de_fichas_agregan_contexto_segun_entidad(client):
    categoria = CategoriaProductoServicio.objects.create(nombre="Fotocopias", descripcion="Impresiones para estudiantes")
    producto = ProductoServicio.objects.create(categoria=categoria, nombre="Cuadernillo", descripcion="Material de estudio")
    actividad = ActividadComercial.objects.create(nombre="Librería", descripcion="Locales con útiles escolares")
    comercio = Comercio.objects.create(
        actividad_comercial=actividad, nombre="Librería Uno", descripcion="Libros y cuadernos",
        beneficio_texto="10 %", estado=Comercio.ESTADO_FIRMADO,
    )
    casos = (
        (categoria, "Impresiones para estudiantes. Una propuesta de la Mutual Escolar UNI2 del CET 3 de General Roca."),
        (producto, "Material de estudio. Disponible en la Mutual Escolar UNI2 del CET 3 de General Roca."),
        (actividad, "Locales con útiles escolares. Conocé los comercios adheridos a la Mutual Escolar UNI2 del CET 3 de General Roca."),
        (comercio, "Libros y cuadernos. Comercio adherido a la Mutual Escolar UNI2 del CET 3 de General Roca."),
    )
    for objeto, descripcion in casos:
        contenido = client.get(objeto.get_absolute_url()).content.decode()
        assert f'name="description" content="{descripcion}"' in contenido
        assert f'<meta property="og:title" content="{objeto.nombre} | UNI2">' in contenido
        assert f'<meta property="og:description" content="{descripcion}">' in contenido


@pytest.mark.django_db
def test_descripcion_que_ya_nombra_uni2_no_agrega_texto(client):
    categoria = CategoriaProductoServicio.objects.create(
        nombre="Fotocopias", descripcion="Impresiones de UNI2 para estudiantes."
    )
    contenido = client.get(categoria.get_absolute_url()).content.decode()
    assert 'name="description" content="Impresiones de UNI2 para estudiantes."' in contenido


@pytest.mark.django_db
def test_listados_publicos_enlazan_fichas_legibles(client):
    categoria = CategoriaProductoServicio.objects.create(nombre="Fotocopias")
    producto = ProductoServicio.objects.create(categoria=categoria, nombre="Impresión")
    actividad = ActividadComercial.objects.create(nombre="Librería")
    comercio = Comercio.objects.create(
        actividad_comercial=actividad, nombre="Librería Uno", descripcion="Libros",
        beneficio_texto="10 %", estado=Comercio.ESTADO_FIRMADO,
    )
    assert producto.get_absolute_url() in client.get("/productos-servicios/").content.decode()
    assert comercio.get_absolute_url() in client.get("/comercios/").content.decode()


@override_settings(UNI2_SITE_URL="https://uni2.app", ALLOWED_HOSTS=["uni2-ashy.vercel.app"])
@pytest.mark.django_db
def test_canonicas_y_sitemap_usan_dominio_publico_aunque_llegue_por_host_tecnico(client):
    home_response = client.get("/", HTTP_HOST="uni2-ashy.vercel.app")
    home = home_response.content.decode()
    sitemap = client.get("/sitemap.xml", HTTP_HOST="uni2-ashy.vercel.app").content.decode()
    robots = client.get("/robots.txt", HTTP_HOST="uni2-ashy.vercel.app").content.decode()
    assert '<link rel="canonical" href="https://uni2.app/">' in home
    assert '<meta property="og:image" content="https://uni2.app/static/pwa/icons/icon-512.png">' in home
    assert '<meta property="og:url" content="https://uni2.app/">' in home
    assert [node["url"] for node in structured_data(home_response)["@graph"]] == [
        "https://uni2.app/", "https://uni2.app/",
    ]
    locations = [node.text for node in ElementTree.fromstring(sitemap).iter() if node.tag.endswith("loc")]
    assert locations and all(url.startswith("https://uni2.app/") for url in locations)
    assert "uni2-ashy.vercel.app" not in sitemap
    assert "Sitemap: https://uni2.app/sitemap.xml" in robots


@override_settings(PWA_ICON_DIRECTORY="pwa/icons/staging")
@pytest.mark.django_db
def test_open_graph_usa_icono_del_entorno(client):
    contenido = client.get("/").content.decode()
    assert '<meta property="og:image" content="http://testserver/static/pwa/icons/staging/icon-512.png">' in contenido
