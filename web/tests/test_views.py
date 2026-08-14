import re
from pathlib import Path

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.staticfiles import finders
from django.urls import reverse
from django.utils import timezone

from asociados.models import CicloLectivo
from comercios.models import ActividadComercial, Comercio
from contenidos.models import CategoriaProductoServicio, ProductoServicio, Publicidad
from cuotas.models import PeriodoCuota


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


@pytest.mark.django_db
def test_home_muestra_el_importe_del_periodo_actual(client):
    hoy = timezone.localdate()
    ciclo = CicloLectivo.objects.create(anio=hoy.year)
    PeriodoCuota.objects.create(
        mes=hoy.month,
        ciclo_lectivo=ciclo,
        importe="1234.56",
        fecha_vencimiento=hoy.replace(day=10),
    )

    contenido = client.get(reverse("web:home")).content.decode()

    assert "$ 1.234,56" in contenido
    assert "$ 700,00" not in contenido


@pytest.mark.django_db
def test_home_sin_periodos_no_inventa_un_importe(client):
    contenido = client.get(reverse("web:home")).content.decode()

    assert "Consultá en la mutual el valor actual de la cuota social." in contenido
    assert "Consultá el valor vigente." in contenido


def test_url_beneficios_no_se_mantiene(client):
    response = client.get("/beneficios/")

    assert response.status_code == 404


@pytest.mark.django_db
def test_navbar_publica_apunta_a_las_secciones_de_la_home(client):
    content = client.get(reverse("web:home")).content.decode()

    assert f'href="{reverse("web:home")}#productos-servicios"' in content
    assert f'href="{reverse("web:home")}#beneficios"' in content
    assert f'href="{reverse("web:productos_servicios")}">Productos y servicios' not in content
    assert f'href="{reverse("web:comercios")}">Comercios' not in content
    assert 'id="productos-servicios"' in content
    assert 'id="beneficios"' in content


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
    hoy = timezone.localdate()
    ciclo = CicloLectivo.objects.create(anio=hoy.year)
    PeriodoCuota.objects.create(
        mes=hoy.month,
        ciclo_lectivo=ciclo,
        importe="1234.56",
        fecha_vencimiento=hoy.replace(day=10),
    )
    client.force_login(user)

    response = client.get(reverse("web:design-system"))

    assert response.status_code == 200
    assert "Sistema visual UNI2" in response.content.decode()
    assert "$ 1.234,56" in response.content.decode()


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
    assert 'id="contacto-preview"' in content
    assert 'aria-label="Ejemplo del footer"' in content
    assert "uni2-theme.js" in content
    assert "style2.css" not in content
    assert "assets/logos/" not in content
    assert "benefit-list-body" in content
    assert "uni2-discount" in content
    assert "uni2-metric-card" in content
    assert "uni2-breadcrumbs" in content
    assert "Fotocopias e impresiones" in content
    assert 'aria-current="page"' in content
    assert "uni2-alert-info" in content
    assert "uni2-alert-success" in content
    assert "uni2-alert-warning" in content
    assert "uni2-alert-danger" in content
    assert "Operación completada" in content
    assert "uni2-status" not in content
    assert "ds-metric" not in content
    assert "ds-status" not in content
    assert "uni2-service-grid" not in content
    assert "web/home.html" in content
    assert "uni2-info-modal" not in content
    assert 'class="card-body"' in content
    assert 'class="service-grid"' not in content
    assert 'class="cta"' not in content
    clases_ds = {
        clase
        for atributo in re.findall(r'class="([^"]*)"', content)
        for clase in atributo.split()
        if clase.startswith("ds-")
    }
    assert clases_ds == set(), f"clases ds-* inesperadas: {clases_ds}"


def test_css_design_system_acota_navegacion_y_no_conserva_aliases_huerfanos():
    css_path = finders.find("css/uni2-design-system.css")
    assert css_path is not None

    css = Path(css_path).read_text(encoding="utf-8")

    # El catálogo usa Bootstrap para su mobiliario y no mantiene una capa CSS paralela.
    assert "ds-page" not in css


def test_catalogo_muestra_todos_los_tokens_publicos():
    project_root = Path(__file__).resolve().parents[2]
    css = (project_root / "static/css/uni2-design-system.css").read_text(encoding="utf-8")
    catalogo = (project_root / "templates/web/design-system.html").read_text(encoding="utf-8")
    prefijos_publicos = (
        "--brand-",
        "--color-",
        "--font-",
        "--letter-spacing-",
        "--line-height-",
        "--motion-",
        "--radius-",
        "--shadow-",
        "--texture-",
    )
    tokens_publicos = {
        token
        for token in re.findall(r"(--[a-z][a-z0-9-]+)\s*:", css)
        if token.startswith(prefijos_publicos)
    }

    faltantes = sorted(token for token in tokens_publicos if token not in catalogo)
    assert faltantes == [], f"tokens públicos ausentes del catálogo: {faltantes}"


def test_css_usa_tokens_canonicos_y_breakpoints_de_bootstrap():
    css_path = finders.find("css/uni2-design-system.css")
    assert css_path is not None
    css = Path(css_path).read_text(encoding="utf-8")

    tokens_historicos = ("--primary:", "--azul:", "--texto:", "--bg:", "--surface:")
    assert all(token not in css for token in tokens_historicos)

    breakpoints = set(re.findall(r"@media \(max-width: ([0-9.]+px)\)", css))
    assert breakpoints == {"575.98px", "767.98px", "991.98px"}


def test_base_carga_una_sola_hoja_css_propia():
    project_root = Path(__file__).resolve().parents[2]
    base = (project_root / "templates/base.html").read_text(encoding="utf-8")
    css_dir = project_root / "static/css"

    assert "css/uni2-design-system.css" in base
    assert not (css_dir / "uni2.css").exists()
    assert not (css_dir / "uni2-v1.css").exists()
    assert not (css_dir / "uni2-v2.css").exists()


def test_base_y_scripts_conservan_contratos_de_accesibilidad():
    project_root = Path(__file__).resolve().parents[2]
    base = (project_root / "templates/base.html").read_text(encoding="utf-8")
    css = (project_root / "static/css/uni2-design-system.css").read_text(encoding="utf-8")
    theme_js = (project_root / "static/js/uni2-theme.js").read_text(encoding="utf-8")
    carousel_js = (project_root / "static/js/uni2-carousel.js").read_text(encoding="utf-8")

    assert base.index("js/uni2-theme.js") < base.index("css/uni2-design-system.css")
    assert 'href="#contenido-principal"' in base
    assert 'id="contenido-principal"' in base
    assert 'aria-label="Modo oscuro"' in base
    assert 'aria-pressed="false"' in base
    assert "applyTheme(preferredTheme(), false)" in theme_js
    assert "prefers-reduced-motion: reduce" in css
    assert "--color-focus-ring" in css
    assert "reducedMotion.matches" in carousel_js
    assert "data-slider-toggle" in carousel_js


def test_design_system_conserva_contraste_de_texto_en_ambos_temas():
    project_root = Path(__file__).resolve().parents[2]
    css = (project_root / "static/css/uni2-design-system.css").read_text(encoding="utf-8")

    def get_block(selector):
        start = css.index(f"{selector} {{")
        return css[start : css.index("\n}", start)]

    def get_tokens(block):
        return dict(re.findall(r"(--[a-z][a-z0-9-]+)\s*:\s*([^;]+);", block))

    def resolve_token(tokens, name):
        value = tokens[name].strip()
        while value.startswith("var("):
            referenced_name = value.removeprefix("var(").removesuffix(")")
            value = tokens[referenced_name].strip()
        return value

    def relative_luminance(color):
        channels = [int(color[index : index + 2], 16) / 255 for index in (1, 3, 5)]
        channels = [
            channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4
            for channel in channels
        ]
        return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]

    def contrast_ratio(foreground, background):
        lighter, darker = sorted(
            (relative_luminance(foreground), relative_luminance(background)),
            reverse=True,
        )
        return (lighter + 0.05) / (darker + 0.05)

    light_tokens = get_tokens(get_block(":root"))
    dark_tokens = light_tokens | get_tokens(get_block('[data-theme="dark"]'))
    text_tokens = (
        "--color-action-on-surface",
        "--color-success-text",
        "--color-warning-text",
        "--color-danger-text",
    )

    for token_name in text_tokens:
        assert contrast_ratio(
            resolve_token(light_tokens, token_name),
            resolve_token(light_tokens, "--color-surface"),
        ) >= 4.5
        assert contrast_ratio(
            resolve_token(dark_tokens, token_name),
            resolve_token(dark_tokens, "--color-surface"),
        ) >= 4.5

    for background_token in ("--brand-yellow", "--brand-green"):
        assert contrast_ratio(
            resolve_token(light_tokens, "--color-on-bright"),
            resolve_token(light_tokens, background_token),
        ) >= 4.5

    assert "color: var(--color-danger-text) !important" in css
    assert "color: var(--step-number-text)" in css


def test_hero_mobile_protege_el_texto_del_fondo_decorativo():
    project_root = Path(__file__).resolve().parents[2]
    css = (project_root / "static/css/uni2-design-system.css").read_text(encoding="utf-8")

    assert ".uni2-hero-layout > div {" in css
    assert "background: var(--color-surface-translucent);" in css
    assert "border: 1px solid var(--color-border-subtle);" in css


def test_paginas_simples_usan_el_shell_responsive_compartido():
    project_root = Path(__file__).resolve().parents[2]
    templates_root = project_root / "templates"
    paginas_simples = (
        "registration/login.html",
        "asociados/credencial.html",
        "asociados/cuotas.html",
        "comercios/validar_credencial.html",
        "comercios/resultado_validacion.html",
    )

    for relative_path in paginas_simples:
        template = (templates_root / relative_path).read_text(encoding="utf-8")
        assert '<div class="container py-5">' in template


def test_service_card_distingue_navegacion_de_contenido_estatico():
    project_root = Path(__file__).resolve().parents[2]
    component = (project_root / "templates/components/service_card.html").read_text(encoding="utf-8")
    css = (project_root / "static/css/uni2-design-system.css").read_text(encoding="utf-8")

    assert '<a class="uni2-service-card {{ color }}" href="{{ url }}">' in component
    assert '<article class="uni2-service-card uni2-service-card-static {{ color }}">' in component
    assert '<span class="link">' in component
    assert '<a class="link"' not in component
    assert "a.uni2-service-card:hover" in css
    assert "button.uni2-service-card:hover" in css
    assert "\n.uni2-service-card:hover {" not in css
    assert ".uni2-service-card-static" in css


def test_catalogo_y_documentacion_reflejan_el_css_productivo():
    project_root = Path(__file__).resolve().parents[2]
    catalogo = (project_root / "templates/web/design-system.html").read_text(encoding="utf-8")
    conceptos = (
        project_root / "especificacion/arquitectura/design-system-conceptos.md"
    ).read_text(encoding="utf-8")
    css = (project_root / "static/css/uni2-design-system.css").read_text(encoding="utf-8")

    assert ".uni2-titulo-seccion — clamp(2.35rem, 6vw, 4.8rem) · peso 900" in catalogo
    assert "grid-template-columns: minmax(0, 0.9fr) minmax(360px, 1.1fr);" in css
    for class_name in (
        "uni2-skip-link",
        "uni2-flash-messages",
        "uni2-service-card-static",
        "uni2-carousel-heading",
        "uni2-carousel-controls",
        "uni2-carousel-dot",
        "uni2-hours-table-compact",
    ):
        assert f"`{class_name}`" in conceptos


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
    assert "$ 400,00" in contenido
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
        descripcion="Útiles, libros y materiales para acompañar el aprendizaje.",
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
    assert 'aria-roledescription="carrusel"' in contenido
    assert 'data-slider-toggle="publicidades-carousel"' in contenido
    assert 'aria-label="Pausar carrusel"' in contenido
    assert 'class="uni2-carousel-dot"' in contenido
    assert 'tabindex="0"' in contenido


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
    assert "data-slider-toggle" not in contenido
    assert "uni2-carousel-dot" not in contenido


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
    assert "uni2-section-heading" in content
    assert "uni2-benefit-band" in content
    assert "uni2-benefit-mix-card" in content
    assert 'class="row g-3"' in content
    assert 'class="benefit-band"' not in content
    assert "uni2-hours-mobile" in content
    assert 'class="service-grid"' not in content


def test_catalogo_y_home_comparten_componentes_visuales():
    project_root = Path(__file__).resolve().parents[2]
    servicios = (project_root / "templates/includes/servicios_grid.html").read_text(encoding="utf-8")
    beneficios = (project_root / "templates/includes/beneficios_grid.html").read_text(encoding="utf-8")
    publicidades = (project_root / "templates/includes/publicidades_grid.html").read_text(encoding="utf-8")
    actividad_detalle = (project_root / "templates/web/actividadcomercial_detalle.html").read_text(encoding="utf-8")
    categoria_detalle = (project_root / "templates/web/categoria_detalle.html").read_text(encoding="utf-8")
    producto_detalle = (project_root / "templates/web/producto_servicio_detalle.html").read_text(encoding="utf-8")
    design_system = (project_root / "templates/web/design-system.html").read_text(encoding="utf-8")

    assert 'class="col-6 col-md-4"' in beneficios
    assert 'components/service_card.html' in servicios
    assert 'components/benefit_card.html' in beneficios
    assert 'components/advertisement_card.html' in publicidades
    assert 'components/benefit_list_item.html' in actividad_detalle
    assert 'components/contact_block.html' in categoria_detalle
    assert 'components/contact_block.html' in producto_detalle
    assert 'components/service_card.html' in design_system
    assert 'components/benefit_card.html' in design_system
    assert 'components/advertisement_card.html' in design_system
    assert 'components/benefit_list_item.html' in design_system
    assert 'components/contact_block.html' in design_system
    assert 'components/breadcrumbs.html' in design_system
    assert 'components/alert.html' in design_system
    assert 'includes/footer.html' in design_system


def test_paginas_de_detalle_comparten_el_componente_breadcrumbs():
    project_root = Path(__file__).resolve().parents[2]
    templates_con_breadcrumbs = (
        "categoria_detalle.html",
        "producto_servicio_detalle.html",
        "comercio_detalle.html",
        "comercio_no_disponible.html",
    )

    for template_name in templates_con_breadcrumbs:
        template = (project_root / "templates/web" / template_name).read_text(encoding="utf-8")
        assert 'components/breadcrumbs.html' in template
        assert '<nav aria-label="breadcrumb">' not in template


def test_breadcrumbs_no_agrega_inicio_ni_conserva_parametros_implicitos():
    project_root = Path(__file__).resolve().parents[2]
    component = (project_root / "templates/components/breadcrumbs.html").read_text(encoding="utf-8")

    assert "Inicio" not in component
    assert "hide_home" not in component
    assert "current_url" not in component
    assert "parent_fragment" not in component
    assert "root_url" in component
    assert "ancestor_url" in component
    assert 'aria-current="page"' in component


def test_anclas_publicas_reservan_espacio_y_permiten_titulos_largos_en_mobile():
    css_path = finders.find("css/uni2-design-system.css")
    assert css_path is not None
    css = Path(css_path).read_text(encoding="utf-8")

    assert ".uni2-anchor-section" in css
    assert 'data-deployment-environment="staging"' in css
    assert "scroll-margin-top" in css
    assert "#productos-servicios .uni2-titulo-seccion" in css
    assert "#beneficios .uni2-titulo-seccion" in css
    assert "overflow-wrap: anywhere" in css


def test_templates_usan_una_sola_familia_productiva_de_alertas():
    project_root = Path(__file__).resolve().parents[2]
    templates_root = project_root / "templates"
    css = (project_root / "static/css/uni2-design-system.css").read_text(encoding="utf-8")
    templates_con_alertas = (
        "includes/messages.html",
        "comercios/resultado_validacion.html",
        "registration/login.html",
        "gestion/importar_cuotas_historicas.html",
        "gestion/importar_asociados.html",
        "gestion/asociados.html",
        "web/design-system/estructura.html",
        "web/design-system.html",
    )

    for relative_path in templates_con_alertas:
        template = (templates_root / relative_path).read_text(encoding="utf-8")
        assert 'components/alert.html' in template

    for template_path in templates_root.rglob("*.html"):
        template = template_path.read_text(encoding="utf-8")
        assert 'class="alert ' not in template

    assert ".alert-success" not in css
    assert ".alert-danger" not in css
    assert ".alert-warning" not in css
    assert ".alert-info" not in css
    assert ".uni2-flash-messages" in css
    assert 'class="uni2-flash-messages"' in (templates_root / "includes/messages.html").read_text(encoding="utf-8")


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
    assert "$ 600,00" in contenido
    assert 'class="uni2-breadcrumbs"' in contenido
    assert 'aria-current="page">Anillado' in contenido
    breadcrumb = re.search(r'<nav class="uni2-breadcrumbs".*?</nav>', contenido, re.DOTALL).group()
    assert f'href="{reverse("web:home")}#productos-servicios">Productos y servicios</a>' in breadcrumb
    assert f'href="{reverse("web:categoria_detalle", args=[categoria.pk])}">Impresiones</a>' in breadcrumb
    assert "Inicio" not in breadcrumb
    assert "← Todos los productos" not in contenido


@pytest.mark.django_db
def test_detalle_comercio_publico_muestra_solo_comercio_firmado(client):
    actividad = ActividadComercial.objects.create(nombre="Librería")
    comercio = Comercio.objects.create(
        nombre="Librería Sur",
        descripcion="Útiles, libros y materiales para acompañar el aprendizaje.",
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
    assert "Útiles, libros y materiales para acompañar el aprendizaje." in contenido
    assert "10% en útiles" in contenido
    assert "Todos los comercios" not in contenido
    assert "Mitre 123" in contenido
    assert "uni2-commerce-identity-logo" in contenido
    assert "uni2-commerce-benefit-block" in contenido
    assert 'class="uni2-commerce-benefit-text"' in contenido
    assert "Visitar online" not in contenido
    assert "Visitar sitio" not in contenido
    assert 'class="uni2-breadcrumbs"' in contenido
    breadcrumb = re.search(r'<nav class="uni2-breadcrumbs".*?</nav>', contenido, re.DOTALL).group()
    assert f'href="{reverse("web:home")}#beneficios">Comercios</a>' in breadcrumb
    assert (
        f'href="{reverse("web:actividad_comercial_detalle", args=[actividad.pk])}">'
        "Librería</a>"
    ) in breadcrumb
    assert "Inicio" not in breadcrumb
    assert 'aria-current="page">Librería Sur' in breadcrumb
    assert response_pendiente.status_code == 200
    contenido_pendiente = response_pendiente.content.decode()
    assert "próximamente" in contenido_pendiente
    breadcrumb_pendiente = re.search(
        r'<nav class="uni2-breadcrumbs".*?</nav>',
        contenido_pendiente,
        re.DOTALL,
    ).group()
    assert f'href="{reverse("web:home")}#beneficios">Comercios</a>' in breadcrumb_pendiente
    assert (
        f'href="{reverse("web:actividad_comercial_detalle", args=[actividad.pk])}">'
        "Librería</a>"
    ) in breadcrumb_pendiente
    assert "Inicio" not in breadcrumb_pendiente
    assert 'aria-current="page">Librería Pendiente' in breadcrumb_pendiente
    assert f'href="{reverse("web:home")}#beneficios" class="uni2-cta uni2-cta-secondary">← Todos los comercios</a>' in contenido_pendiente


@pytest.mark.django_db
def test_detalle_comercio_sin_direccion_no_muestra_bloque_vacio(client):
    actividad = ActividadComercial.objects.create(nombre="Venta online")
    comercio = Comercio.objects.create(
        nombre="Emprendimiento virtual",
        descripcion="Productos disponibles exclusivamente por internet.",
        actividad_comercial=actividad,
        beneficio_texto="10% en compras online",
        estado=Comercio.ESTADO_FIRMADO,
        direccion="",
    )

    response = client.get(reverse("web:comercio_detalle", args=[comercio.id]))

    contenido = response.content.decode()
    assert response.status_code == 200
    assert "Emprendimiento virtual" in contenido
    assert "<h2>Dirección</h2>" not in contenido


@pytest.mark.django_db
def test_comercios_publicos_muestran_actividad_comercial(client):
    actividad = ActividadComercial.objects.create(nombre="Librería")
    Comercio.objects.create(
        nombre="Librería Zeta",
        descripcion="Útiles escolares y materiales de estudio.",
        direccion="Mitre 123",
        actividad_comercial=actividad,
        beneficio_texto="10% en útiles",
        estado=Comercio.ESTADO_FIRMADO,
        orden=1,
    )
    Comercio.objects.create(
        nombre="Librería Alfa",
        descripcion="Papelería y servicio de anillado.",
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
    assert (
        response.context["bloques_productos"]["generales"]["grupos_precio"][0]["items"][0].nombre
        == "Fotocopia simple"
    )
    contenido = response.content.decode()
    assert "Fotocopias" in contenido
    assert "Fotocopia simple" in contenido
    assert "Inactivo" not in contenido
    assert "$ 50,00" in contenido
    assert "Consultá en la mutual" in contenido
    assert 'class="uni2-print-contact-body"' in contenido
    assert 'class="uni2-category-detail-layout"' in contenido
    assert 'class="uni2-detail-layout"' not in contenido
    assert 'aria-labelledby="productos-generales-title"' not in contenido
    assert contenido.index('id="categoria-title"') < contenido.index('class="uni2-category-products-panel"')
    assert 'class="uni2-breadcrumbs"' in contenido
    assert 'aria-current="page">Fotocopias' in contenido


@pytest.mark.django_db
def test_categoria_detalle_presenta_fotos_imagen_informativa_y_cuatro_casos_de_precio(client):
    categoria = CategoriaProductoServicio.objects.create(
        nombre="Uniformes",
        descripcion="Prendas institucionales.",
        titulo_imagen_informativa="Tabla de talles",
        imagen_informativa="categorias_productos_servicios/talles.webp",
    )
    diferenciado = ProductoServicio.objects.create(
        categoria=categoria,
        nombre="Remera",
        descripcion="Remera institucional.",
        foto="productos_servicios/remera.webp",
        ciclo_destinatario="CB",
        curso_destinatario="1ro",
        precio_asociados=9000,
        precio_no_asociados=12000,
        orden=1,
    )
    unico = ProductoServicio.objects.create(
        categoria=categoria,
        nombre="Escudo",
        descripcion="Escudo bordado.",
        precio_asociados=5000,
        precio_no_asociados=5000,
        orden=2,
    )
    solo_asociados = ProductoServicio.objects.create(
        categoria=categoria,
        nombre="Buzo",
        descripcion="Buzo institucional.",
        precio_asociados=18000,
        precio_no_asociados=None,
        orden=3,
    )
    servicio = ProductoServicio.objects.create(
        categoria=categoria,
        nombre="Prueba de talle",
        descripcion="Asesoramiento presencial.",
        es_servicio=True,
        precio_asociados=None,
        precio_no_asociados=None,
        orden=4,
    )
    servicio_con_precio = ProductoServicio.objects.create(
        categoria=categoria,
        nombre="Ajuste de uniforme",
        descripcion="Servicio de costura.",
        es_servicio=True,
        precio_asociados=2000,
        precio_no_asociados=2500,
        orden=5,
    )
    superior = ProductoServicio.objects.create(
        categoria=categoria,
        nombre="Campera superior",
        descripcion="Campera para ciclo superior.",
        ciclo_destinatario="CS",
        curso_destinatario="1ro",
        precio_asociados=22000,
        precio_no_asociados=26000,
        orden=6,
    )

    contenido = client.get(reverse("web:categoria_detalle", args=[categoria.pk])).content.decode()

    assert 'data-price-type="diferenciado"' in contenido
    assert 'data-price-type="unico"' in contenido
    assert 'data-price-type="solo_asociados"' in contenido
    assert 'data-price-type="sin_precio"' in contenido
    assert "Precio asociado" in contenido
    assert "Precio no asociado" in contenido
    assert "Solo asociados" in contenido
    assert "Sin precio" in contenido
    assert "$ 0,00" not in contenido
    assert f'href="{reverse("web:producto_servicio_detalle", args=[diferenciado.pk])}"' in contenido
    assert f'href="{reverse("web:producto_servicio_detalle", args=[unico.pk])}"' in contenido
    assert f'href="{reverse("web:producto_servicio_detalle", args=[solo_asociados.pk])}"' in contenido
    assert f'href="{reverse("web:producto_servicio_detalle", args=[servicio.pk])}"' in contenido
    assert f'href="{reverse("web:producto_servicio_detalle", args=[servicio_con_precio.pk])}"' in contenido
    assert f'href="{reverse("web:producto_servicio_detalle", args=[superior.pk])}"' in contenido
    filas = re.findall(r'<tr class="uni2-product-row">.*?</tr>', contenido, re.DOTALL)
    assert len(filas) == 6
    assert all(fila.count("href=") == 1 for fila in filas)
    assert ">Producto</th>" in contenido
    assert ">Servicio</th>" in contenido
    assert "Disponibilidad" not in contenido
    tabla_sin_precio = re.search(
        r'<table[^>]+data-price-type="sin_precio".*?</table>',
        contenido,
        re.DOTALL,
    ).group()
    assert tabla_sin_precio.count('scope="col"') == 1
    assert "<td" not in tabla_sin_precio
    assert 'class="uni2-price-column"' in contenido
    assert 'scope="col"' in contenido
    assert 'scope="row"' in contenido
    assert 'aria-label="1.º C.B. · Precio diferenciado"' in contenido
    assert 'aria-label="Productos generales · Precio único"' in contenido
    assert '/media/productos_servicios/remera.webp' in contenido
    assert 'class="uni2-category-detail-layout"' in contenido
    assert 'class="uni2-detail-layout"' not in contenido
    assert contenido.index('id="categoria-title"') < contenido.index('class="uni2-category-products-panel"')
    assert "Ciclo Básico" in contenido
    assert "Ciclo Superior" in contenido
    assert "1.º C.B." in contenido
    assert "1.º C.S." in contenido
    assert 'data-cycle-selector' in contenido
    assert 'class="uni2-general-products-card"' in contenido
    assert 'class="uni2-cycles-grid uni2-cycles-grid--multiple"' in contenido
    assert 'class="uni2-cycle-section uni2-cycle-card uni2-cycle-card--cb"' in contenido
    assert 'class="uni2-cycle-section uni2-cycle-card uni2-cycle-card--cs"' in contenido
    assert 'role="tablist"' in contenido
    assert 'data-cycle-tab="cb"' in contenido
    assert 'aria-controls="uni2-cycle-panel-cb"' in contenido
    assert 'data-cycle-tab="cs"' in contenido
    assert 'aria-controls="uni2-cycle-panel-cs"' in contenido
    assert 'id="uni2-cycle-panel-cb"' in contenido
    assert 'id="uni2-cycle-panel-cs"' in contenido
    assert 'src="/static/js/uni2-cycle-selector.js"' in contenido
    assert "Tabla de talles" in contenido
    assert '/media/categorias_productos_servicios/talles.webp' in contenido


@pytest.mark.django_db
def test_categoria_con_un_solo_ciclo_no_muestra_selector_mobile(client):
    categoria = CategoriaProductoServicio.objects.create(nombre="Cuadernillos")
    ProductoServicio.objects.create(
        categoria=categoria,
        nombre="Matemática",
        descripcion="Cuadernillo de Matemática.",
        ciclo_destinatario="CB",
        curso_destinatario="1ro",
        precio_asociados=4000,
        precio_no_asociados=5000,
    )

    contenido = client.get(reverse("web:categoria_detalle", args=[categoria.pk])).content.decode()

    assert 'role="tablist"' not in contenido
    assert 'class="uni2-cycles-grid"' in contenido
    assert "uni2-cycles-grid--multiple" not in contenido
    assert 'class="uni2-cycle-section uni2-cycle-card uni2-cycle-card--cb"' in contenido
    assert 'id="uni2-cycle-panel-cb"' in contenido
    assert "1.º C.B." in contenido


@pytest.mark.django_db
def test_detalle_producto_muestra_foto_destinatario_e_imagen_informativa(client):
    categoria = CategoriaProductoServicio.objects.create(
        nombre="Uniformes",
        titulo_imagen_informativa="Tabla de talles",
        imagen_informativa="categorias_productos_servicios/talles.webp",
    )
    producto = ProductoServicio.objects.create(
        categoria=categoria,
        nombre="Remera",
        descripcion="Remera institucional.",
        foto="productos_servicios/remera.webp",
        ciclo_destinatario="CB",
        curso_destinatario="1ro",
        precio_asociados=9000,
        precio_no_asociados=12000,
    )

    contenido = client.get(reverse("web:producto_servicio_detalle", args=[producto.pk])).content.decode()

    assert 'class="uni2-product-photo"' in contenido
    assert 'class="uni2-detail-layout"' in contenido
    assert '/media/productos_servicios/remera.webp' in contenido
    assert "Ciclo Básico · 1ro" in contenido
    assert "Tabla de talles" in contenido
    assert '/media/categorias_productos_servicios/talles.webp' in contenido
    assert contenido.index("Remera institucional.") < contenido.index('class="uni2-product-photo"')
    assert "← Todos los productos" not in contenido


@pytest.mark.django_db
def test_detalles_adaptan_presentacion_a_precio_unico_solo_asociados_y_servicio_sin_precio(client):
    categoria = CategoriaProductoServicio.objects.create(nombre="Servicios")
    unico = ProductoServicio.objects.create(
        categoria=categoria,
        nombre="Credencial",
        descripcion="Reposición.",
        precio_asociados=5000,
        precio_no_asociados=5000,
    )
    exclusivo = ProductoServicio.objects.create(
        categoria=categoria,
        nombre="Beneficio exclusivo",
        descripcion="Solo para asociados.",
        precio_asociados=3000,
        precio_no_asociados=None,
    )
    sin_precio = ProductoServicio.objects.create(
        categoria=categoria,
        nombre="Orientación",
        descripcion="Atención personalizada.",
        es_servicio=True,
        precio_asociados=None,
        precio_no_asociados=None,
    )

    contenido_unico = client.get(reverse("web:producto_servicio_detalle", args=[unico.pk])).content.decode()
    contenido_exclusivo = client.get(reverse("web:producto_servicio_detalle", args=[exclusivo.pk])).content.decode()
    contenido_sin_precio = client.get(reverse("web:producto_servicio_detalle", args=[sin_precio.pk])).content.decode()

    assert "Precio general" in contenido_unico
    assert contenido_unico.count("$ 5.000,00") == 1
    assert "Solo asociados" in contenido_exclusivo
    assert "Precio asociado" in contenido_exclusivo
    assert "¿Cómo acceder?" in contenido_sin_precio
    assert "Sin precio" in contenido_sin_precio
    assert "$ 0,00" not in contenido_sin_precio


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
    actividad = ActividadComercial.objects.create(
        nombre="Gastronomía",
        descripcion="Sabores y opciones para disfrutar en cada momento.",
    )
    parrilla = Comercio.objects.create(
        nombre="Parrilla Don Pancho",
        descripcion="Carnes a la parrilla y platos para compartir.",
        direccion="Mitre 100",
        actividad_comercial=actividad,
        beneficio_texto="10% de descuento",
        estado=Comercio.ESTADO_FIRMADO,
        orden=1,
        foto=SimpleUploadedFile("parrilla.jpg", b"content", content_type="image/jpeg"),
    )
    Comercio.objects.create(
        nombre="Lo de Carlitos",
        descripcion="Milanesas y comidas caseras.",
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
    assert "uni2-discount" in contenido
    assert 'class="uni2-breadcrumbs"' in contenido
    breadcrumb = re.search(r'<nav class="uni2-breadcrumbs".*?</nav>', contenido, re.DOTALL).group()
    assert f'href="{reverse("web:home")}#beneficios">Comercios</a>' in breadcrumb
    assert 'aria-current="page">Gastronomía' in breadcrumb
    assert f'href="{url}">Gastronomía</a>' not in breadcrumb
    assert "Inicio" not in breadcrumb
    assert "Actividad comercial" not in contenido
    assert "Sabores y opciones para disfrutar en cada momento." in contenido
    assert "Parrilla Don Pancho" in contenido
    assert "Carnes a la parrilla y platos para compartir." in contenido
    assert "10% de descuento" in contenido
    assert "Lo de Carlitos" in contenido
    assert "Milanesas y comidas caseras." in contenido
    detalle_parrilla_url = reverse("web:comercio_detalle", args=[parrilla.pk])
    assert (
        f'<a class="uni2-benefit-detail-link js-commerce-modal-link"\n'
        f'               href="{detalle_parrilla_url}"' in contenido
    )
    assert contenido.count(f'href="{detalle_parrilla_url}"') == 1
    assert "No Visible" not in contenido


@pytest.mark.django_db
def test_visitar_online_abre_la_presencia_web_en_una_pestania_nueva(client):
    actividad = ActividadComercial.objects.create(nombre="Venta online")
    presencia_web = "https://www.instagram.com/emprendimiento.prueba/"
    comercio = Comercio.objects.create(
        nombre="Emprendimiento de prueba",
        descripcion="Productos disponibles por internet.",
        actividad_comercial=actividad,
        beneficio_texto="10% en compras",
        estado=Comercio.ESTADO_FIRMADO,
        url_presencia_web=presencia_web,
    )
    expected_link = re.compile(
        rf'<a[^>]+href="{re.escape(presencia_web)}"'
        r'[^>]+target="_blank"[^>]+rel="noopener noreferrer"[^>]*>'
    )

    page_urls = (
        reverse("web:comercios"),
        reverse("web:comercio_detalle", args=[comercio.pk]),
        reverse("web:actividad_comercial_detalle", args=[actividad.pk]),
    )
    for page_url in page_urls:
        response = client.get(page_url)
        content = response.content.decode()

        assert response.status_code == 200
        assert expected_link.search(content)

    assert reverse("web:comercio_detalle", args=[comercio.pk]) in content


@pytest.mark.django_db
def test_actividad_comercial_detalle_404_sin_comercios_o_inexistente(client):
    actividad = ActividadComercial.objects.create(nombre="Vacía")

    response = client.get(reverse("web:actividad_comercial_detalle", args=[actividad.pk]))
    assert response.status_code == 404

    response = client.get(reverse("web:actividad_comercial_detalle", args=[999]))
    assert response.status_code == 404
