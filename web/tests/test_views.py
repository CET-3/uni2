import pytest
from django.urls import reverse

from comercios.models import ActividadComercial, Comercio
from contenidos.models import Beneficio


@pytest.mark.django_db
@pytest.mark.parametrize(
    "url_name",
    [
        "web:home",
        "web:beneficios",
        "web:comercios",
    ],
)
def test_paginas_publicas_responden(client, url_name):
    response = client.get(reverse(url_name))
    assert response.status_code == 200


@pytest.mark.django_db
def test_beneficios_publicos_muestran_activos_ordenados(client):
    Beneficio.objects.create(titulo="Tercero", descripcion="Visible tercero", activo=True, orden=3)
    Beneficio.objects.create(titulo="Inactivo", descripcion="No visible", activo=False, orden=1)
    Beneficio.objects.create(titulo="Primero", descripcion="Visible primero", activo=True, orden=1)
    Beneficio.objects.create(titulo="Segundo", descripcion="Visible segundo", activo=True, orden=2)

    response = client.get(reverse("web:beneficios"))

    contenido = response.content.decode()
    assert contenido.index("Primero") < contenido.index("Segundo") < contenido.index("Tercero")
    assert "Inactivo" not in contenido


@pytest.mark.django_db
def test_comercios_publicos_muestran_actividad_comercial(client):
    actividad = ActividadComercial.objects.create(nombre="Librería")
    Comercio.objects.create(
        nombre="Librería Zeta",
        direccion="Mitre 123",
        actividad_comercial=actividad,
        beneficio_texto="10% en útiles",
        estado=Comercio.ESTADO_FIRMADO,
    )
    Comercio.objects.create(
        nombre="Librería Alfa",
        direccion="San Martín 55",
        actividad_comercial=actividad,
        beneficio_texto="2x1 en anillados",
        estado=Comercio.ESTADO_FIRMADO,
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
    assert contenido.index("Librería Alfa") < contenido.index("Librería Zeta")
    assert "Actividad:" in contenido
    assert "Librería" in contenido
    assert "Librería Pendiente" not in contenido
