from django.contrib import admin

from comercios.admin import ActividadComercialAdmin, ComercioAdmin
from comercios.models import ActividadComercial, Comercio


def test_admin_actividad_comercial_muestra_nombre_y_descripcion():
    actividad_admin = ActividadComercialAdmin(ActividadComercial, admin.site)

    assert actividad_admin.list_display == ("nombre", "descripcion")
    assert actividad_admin.fields == ("nombre", "descripcion")
    assert actividad_admin.list_display_links == ("nombre",)


def test_admin_comercio_enlaza_el_nombre_desde_el_listado():
    comercio_admin = ComercioAdmin(Comercio, admin.site)

    assert comercio_admin.list_display_links == ("nombre",)


def test_admin_comercio_muestra_primero_los_datos_principales():
    comercio_admin = ComercioAdmin(Comercio, admin.site)

    assert comercio_admin.fields[:6] == (
        "actividad_comercial",
        "nombre",
        "descripcion",
        "beneficio_texto",
        "estado",
        "orden",
    )
    assert comercio_admin.fields[1:3] == ("nombre", "descripcion")
