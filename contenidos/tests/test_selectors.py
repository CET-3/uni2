import pytest
from django.core.exceptions import ValidationError

from comercios.models import ActividadComercial, Comercio
from contenidos.models import CategoriaProductoServicio, ProductoServicio, Publicidad
from contenidos.selectors import (
    get_bloques_productos_publicos,
    get_categorias_productos_servicios_publicas,
    get_publicidades_home,
)


def crear_producto(categoria, nombre, **cambios):
    datos = {
        "categoria": categoria,
        "nombre": nombre,
        "descripcion": nombre,
        "precio_asociados": 100,
        "precio_no_asociados": 150,
    }
    datos.update(cambios)
    return ProductoServicio.objects.create(**datos)


@pytest.mark.django_db
def test_get_categorias_productos_servicios_publicas_solo_activas_con_items_activos():
    categoria_visible = CategoriaProductoServicio.objects.create(
        nombre="Fotocopias",
        descripcion="Servicios de impresión",
        texto_cta="Consultá disponibilidad uni2mutual@gmail.com",
        activa=True,
        orden=1,
    )
    categoria_inactiva = CategoriaProductoServicio.objects.create(
        nombre="Inactiva",
        descripcion="No visible",
        activa=False,
        orden=2,
    )
    ProductoServicio.objects.create(
        categoria=categoria_visible,
        nombre="Anillado",
        descripcion="Anillado simple",
        precio_asociados=1000,
        precio_no_asociados=1500,
        activo=True,
    )
    ProductoServicio.objects.create(
        categoria=categoria_visible,
        nombre="Oculto",
        descripcion="No visible",
        precio_asociados=1000,
        precio_no_asociados=1500,
        activo=False,
    )
    ProductoServicio.objects.create(
        categoria=categoria_inactiva,
        nombre="Producto inactivo",
        descripcion="No visible",
        precio_asociados=1000,
        precio_no_asociados=1500,
        activo=True,
    )

    resultado = list(get_categorias_productos_servicios_publicas())

    assert len(resultado) == 1
    assert resultado[0].nombre == "Fotocopias"
    assert [item.nombre for item in resultado[0].items_publicos] == ["Anillado"]


@pytest.mark.django_db
def test_get_categorias_productos_servicios_publicas_ordenadas_con_items_ordenados():
    segunda = CategoriaProductoServicio.objects.create(nombre="Segunda", descripcion="Segunda", activa=True, orden=2)
    primera = CategoriaProductoServicio.objects.create(nombre="Primera", descripcion="Primera", activa=True, orden=1)
    ProductoServicio.objects.create(
        categoria=primera,
        nombre="Segundo item",
        descripcion="Segundo",
        precio_asociados=1000,
        precio_no_asociados=1500,
        activo=True,
        orden=2,
    )
    ProductoServicio.objects.create(
        categoria=primera,
        nombre="Primer item",
        descripcion="Primero",
        precio_asociados=1000,
        precio_no_asociados=1500,
        activo=True,
        orden=1,
    )
    ProductoServicio.objects.create(
        categoria=segunda,
        nombre="Otro item",
        descripcion="Otro",
        precio_asociados=1000,
        precio_no_asociados=1500,
        activo=True,
        orden=1,
    )

    resultado = list(get_categorias_productos_servicios_publicas())

    assert [categoria.nombre for categoria in resultado] == ["Primera", "Segunda"]
    assert [item.nombre for item in resultado[0].items_publicos] == ["Primer item", "Segundo item"]


@pytest.mark.django_db
def test_get_publicidades_home_solo_activas_ordenadas_y_con_vinculos():
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
        actividad_comercial=actividad,
        nombre="Librería Sur",
        beneficio_texto="10% en útiles",
        estado=Comercio.ESTADO_FIRMADO,
        direccion="Mitre 123",
    )
    Publicidad.objects.create(
        titulo="Oculta",
        descripcion="No visible",
        etiqueta_principal="Promo",
        etiqueta_secundaria="OFF",
        foto="publicidades/oculta.webp",
        activa=False,
        orden=1,
    )
    Publicidad.objects.create(
        titulo="Producto destacado",
        descripcion="Anillado para apuntes",
        etiqueta_principal="Servicio",
        etiqueta_secundaria="Nuevo",
        foto="publicidades/anillado.webp",
        producto_servicio=producto,
        activa=True,
        orden=2,
    )
    Publicidad.objects.create(
        titulo="Comercio destacado",
        descripcion="Librería adherida",
        etiqueta_principal="Comercio",
        etiqueta_secundaria="10% OFF",
        foto="publicidades/libreria.webp",
        comercio=comercio,
        activa=True,
        orden=1,
    )

    resultado = list(get_publicidades_home())

    assert [publicidad.titulo for publicidad in resultado] == ["Comercio destacado", "Producto destacado"]
    assert resultado[0].comercio == comercio
    assert resultado[1].producto_servicio == producto


@pytest.mark.django_db
def test_publicidad_con_comercio_pendiente_no_se_muestra_en_home():
    actividad = ActividadComercial.objects.create(nombre="Librería")
    comercio_firmado = Comercio.objects.create(
        actividad_comercial=actividad,
        nombre="Librería Sur",
        beneficio_texto="10% en útiles",
        estado=Comercio.ESTADO_FIRMADO,
        direccion="Mitre 123",
    )
    comercio_pendiente = Comercio.objects.create(
        actividad_comercial=actividad,
        nombre="Librería Norte",
        beneficio_texto="15% en libros",
        estado=Comercio.ESTADO_PENDIENTE,
        direccion="Av. Siempre Viva 742",
    )
    publicidad_visible = Publicidad.objects.create(
        titulo="Comercio firmado",
        descripcion="Visible",
        etiqueta_principal="Comercio",
        etiqueta_secundaria="10% OFF",
        foto="publicidades/firmado.webp",
        comercio=comercio_firmado,
        activa=True,
        orden=1,
    )
    Publicidad.objects.create(
        titulo="Comercio pendiente",
        descripcion="No visible",
        etiqueta_principal="Comercio",
        etiqueta_secundaria="15% OFF",
        foto="publicidades/pendiente.webp",
        comercio=comercio_pendiente,
        activa=True,
        orden=2,
    )

    resultado = list(get_publicidades_home())

    assert len(resultado) == 1
    assert resultado[0] == publicidad_visible


@pytest.mark.django_db
def test_publicidad_no_puede_vincular_producto_y_comercio_a_la_vez():
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
        actividad_comercial=actividad,
        nombre="Librería Sur",
        beneficio_texto="10% en útiles",
        estado=Comercio.ESTADO_FIRMADO,
        direccion="Mitre 123",
    )
    publicidad = Publicidad(
        titulo="Destino doble",
        descripcion="No válido",
        etiqueta_principal="Promo",
        etiqueta_secundaria="OFF",
        foto="publicidades/doble.webp",
        producto_servicio=producto,
        comercio=comercio,
    )

    with pytest.raises(ValidationError, match="no puede estar vinculada"):
        publicidad.full_clean()


@pytest.mark.django_db
def test_bloques_separan_generales_ciclos_y_cursos():
    categoria = CategoriaProductoServicio.objects.create(nombre="Cuadernillos")
    crear_producto(categoria, "General", orden=1)
    crear_producto(categoria, "Todo CB", ciclo_destinatario="CB", orden=2)
    crear_producto(
        categoria,
        "Primero",
        ciclo_destinatario="CB",
        curso_destinatario="1ro",
        orden=3,
    )
    crear_producto(
        categoria,
        "Segundo",
        ciclo_destinatario="CB",
        curso_destinatario="2do",
        orden=4,
    )
    crear_producto(
        categoria,
        "Superior",
        ciclo_destinatario="CS",
        curso_destinatario="1ro",
        orden=5,
    )

    catalogo = get_bloques_productos_publicos(categoria)

    assert catalogo["generales"]["grupos_precio"][0]["items"][0].nombre == "General"
    assert [ciclo["codigo"] for ciclo in catalogo["ciclos"]] == ["CB", "CS"]
    assert [grupo["titulo"] for grupo in catalogo["ciclos"][0]["grupos"]] == [
        "Para todo el ciclo",
        "1.º C.B.",
        "2.º C.B.",
    ]
    assert [grupo["grupos_precio"][0]["items"][0].nombre for grupo in catalogo["ciclos"][0]["grupos"]] == [
        "Todo CB",
        "Primero",
        "Segundo",
    ]
    assert [grupo["titulo"] for grupo in catalogo["ciclos"][1]["grupos"]] == ["1.º C.S."]
    assert catalogo["mostrar_selector_ciclos"] is True


@pytest.mark.django_db
def test_catalogo_con_un_solo_ciclo_no_muestra_selector():
    categoria = CategoriaProductoServicio.objects.create(nombre="Fotocopias")
    crear_producto(categoria, "Simple", ciclo_destinatario="CB")

    catalogo = get_bloques_productos_publicos(categoria)

    assert catalogo["generales"] is None
    assert [ciclo["codigo"] for ciclo in catalogo["ciclos"]] == ["CB"]
    assert catalogo["mostrar_selector_ciclos"] is False


@pytest.mark.django_db
def test_catalogo_vacio_devuelve_estructura_sin_bloques():
    categoria = CategoriaProductoServicio.objects.create(nombre="Fotocopias")

    assert get_bloques_productos_publicos(categoria) == {
        "generales": None,
        "ciclos": [],
        "mostrar_selector_ciclos": False,
    }


@pytest.mark.django_db
def test_bloques_excluyen_productos_inactivos():
    categoria = CategoriaProductoServicio.objects.create(nombre="Uniformes")
    crear_producto(categoria, "Visible", activo=True)
    crear_producto(categoria, "Oculto", activo=False)

    catalogo = get_bloques_productos_publicos(categoria)

    nombres = [item.nombre for grupo in catalogo["generales"]["grupos_precio"] for item in grupo["items"]]
    assert nombres == ["Visible"]


@pytest.mark.django_db
def test_bloques_respetan_orden_y_nombre():
    categoria = CategoriaProductoServicio.objects.create(nombre="Uniformes")
    crear_producto(categoria, "Zeta", orden=2)
    crear_producto(categoria, "Beta", orden=1)
    crear_producto(categoria, "Alfa", orden=1)

    catalogo = get_bloques_productos_publicos(categoria)

    assert [item.nombre for item in catalogo["generales"]["grupos_precio"][0]["items"]] == [
        "Alfa",
        "Beta",
        "Zeta",
    ]


@pytest.mark.django_db
def test_bloques_separan_escenarios_contiguos_sin_reordenar():
    categoria = CategoriaProductoServicio.objects.create(nombre="Uniformes")
    crear_producto(categoria, "Diferenciado A", orden=1)
    crear_producto(categoria, "Único", precio_asociados=200, precio_no_asociados=200, orden=2)
    crear_producto(categoria, "Diferenciado B", orden=3)

    catalogo = get_bloques_productos_publicos(categoria)
    grupos = catalogo["generales"]["grupos_precio"]

    assert [grupo["tipo_precio"] for grupo in grupos] == ["diferenciado", "unico", "diferenciado"]
    assert [[item.nombre for item in grupo["items"]] for grupo in grupos] == [
        ["Diferenciado A"],
        ["Único"],
        ["Diferenciado B"],
    ]


@pytest.mark.django_db
def test_grupos_de_precio_deducen_si_contienen_productos_servicios_o_ambos():
    categoria_productos = CategoriaProductoServicio.objects.create(nombre="Productos")
    crear_producto(categoria_productos, "Remera")

    categoria_servicios = CategoriaProductoServicio.objects.create(nombre="Servicios")
    crear_producto(categoria_servicios, "Anillado", es_servicio=True)

    categoria_mixta = CategoriaProductoServicio.objects.create(nombre="Mixta")
    crear_producto(categoria_mixta, "Cuadernillo", orden=1)
    crear_producto(categoria_mixta, "Anillado", es_servicio=True, orden=2)

    grupo_productos = get_bloques_productos_publicos(categoria_productos)["generales"]["grupos_precio"][0]
    grupo_servicios = get_bloques_productos_publicos(categoria_servicios)["generales"]["grupos_precio"][0]
    grupo_mixto = get_bloques_productos_publicos(categoria_mixta)["generales"]["grupos_precio"][0]

    assert grupo_productos["etiqueta_items"] == "Producto"
    assert grupo_servicios["etiqueta_items"] == "Servicio"
    assert grupo_mixto["etiqueta_items"] == "Producto o servicio"
