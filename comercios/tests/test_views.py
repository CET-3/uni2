from datetime import date

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse

from asociados.models import Asociado
from asociados.services import create_asociado
from comercios.models import ActividadComercial, Comercio
from usuarios.roles import COMERCIO_GROUP


@pytest.mark.django_db
def test_pantalla_validacion_presenta_un_puesto_de_control_destacado(client):
    user = get_user_model().objects.create_user(username="com-control", password="secreto123")
    actividad = ActividadComercial.objects.create(nombre="Papelería control")
    Comercio.objects.create(
        nombre="Papelera Control",
        usuario=user,
        actividad_comercial=actividad,
        estado=Comercio.ESTADO_FIRMADO,
    )
    client.force_login(user)

    content = client.get(reverse("comercios:validar_credencial")).content.decode()

    assert 'class="uni2-validation-station"' in content
    assert 'class="uni2-validation-spotlight"' in content
    assert 'class="uni2-validation-panel"' in content
    assert "DNI o código de credencial" in content
    assert 'class="btn btn-primary uni2-validation-submit"' in content


@pytest.mark.django_db
def test_validacion_credencial_comercio(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="com2", password="secreto123")
    actividad = ActividadComercial.objects.create(nombre="Papeleria")
    Comercio.objects.create(
        nombre="Papelera Centro",
        direccion="San Martin 55",
        usuario=user,
        actividad_comercial=actividad,
        beneficio_texto="15% en fotocopias",
        estado=Comercio.ESTADO_FIRMADO,
    )
    asociado = create_asociado(
        nombre="Eva",
        apellido="Lopez",
        dni="40333999",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta="2026-05-10",
    )

    client.force_login(user)
    response = client.post(
        reverse("comercios:validar_credencial"),
        {"identificador": str(asociado.token_credencial)},
    )

    assert response.status_code == 200
    content = response.content.decode()
    assert "Credencial activa" in content
    assert "Asociado" in content
    assert asociado.dni in content
    assert "Identidad presentada" not in content
    assert f'<p class="uni2-validation-person-dni">DNI {asociado.dni}</p>' in content
    assert "uni2-validation-result-active" in content
    assert 'role="status"' in content
    assert "uni2-alert" not in content


@pytest.mark.django_db
def test_validacion_credencial_comercio_por_dni(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="com-dni", password="secreto123")
    actividad = ActividadComercial.objects.create(nombre="Papelería DNI")
    Comercio.objects.create(
        nombre="Papelera DNI",
        usuario=user,
        actividad_comercial=actividad,
        estado=Comercio.ESTADO_FIRMADO,
    )
    asociado = create_asociado(
        nombre="Nora",
        apellido="Díaz",
        dni="40334001",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta="2026-05-10",
    )
    client.force_login(user)

    response = client.post(
        reverse("comercios:validar_credencial"),
        {"identificador": asociado.dni},
    )

    assert response.status_code == 200
    assert "Credencial activa" in response.content.decode()
    assert "Nora Díaz" in response.content.decode()


@pytest.mark.django_db
def test_resultado_invalido_usa_el_estado_visual_de_rechazo(client):
    user = get_user_model().objects.create_user(username="com-invalida", password="secreto123")
    actividad = ActividadComercial.objects.create(nombre="Papelería inválida")
    Comercio.objects.create(
        nombre="Papelera Inválida",
        usuario=user,
        actividad_comercial=actividad,
        estado=Comercio.ESTADO_FIRMADO,
    )
    client.force_login(user)

    response = client.post(
        reverse("comercios:validar_credencial"),
        {"identificador": "99999999"},
    )
    content = response.content.decode()

    assert "Credencial inválida" in content
    assert "uni2-validation-result-danger" in content
    assert "Revisá el DNI o código e intentá nuevamente" in content


@pytest.mark.django_db
def test_mi_convenio_muestra_los_datos_del_comercio_vinculado(client):
    user = get_user_model().objects.create_user(username="mi-convenio", password="secreto123")
    actividad = ActividadComercial.objects.create(nombre="Librería")
    comercio = Comercio.objects.create(
        nombre="Librería del Centro",
        actividad_comercial=actividad,
        usuario=user,
        descripcion="Libros y materiales escolares",
        propietario="Ana Referente",
        beneficio_texto="15% en compras en efectivo",
        estado=Comercio.ESTADO_FIRMADO,
        fecha_convenio=date(2026, 3, 30),
        email="comercio@example.com",
        telefono="291 555-0101",
        direccion="San Martín 55",
        ciudad="Bahía Blanca",
        provincia="Buenos Aires",
        url_presencia_web="https://example.com/comercio",
        orden=9876,
        latitud="-38.700000",
        longitud="-62.200000",
    )
    client.force_login(user)

    response = client.get(reverse("comercios:mi_convenio"))
    content = response.content.decode()

    assert response.status_code == 200
    assert response.context["comercio"] == comercio
    for expected in (
        "Librería del Centro",
        "Librería",
        "Libros y materiales escolares",
        "Ana Referente",
        "Firmado",
        "30/03/2026",
        "15% en compras en efectivo",
        "comercio@example.com",
        "291 555-0101",
        "San Martín 55",
        "Bahía Blanca",
        "Buenos Aires",
        "https://example.com/comercio",
    ):
        assert expected in content
    assert "9876" not in content
    assert "-38.700000" not in content
    assert "-62.200000" not in content
    assert 'target="_blank"' in content
    assert 'rel="noopener noreferrer"' in content


@pytest.mark.django_db
@pytest.mark.parametrize("estado", [valor for valor, _ in Comercio.ESTADOS])
def test_mi_convenio_se_puede_consultar_en_todos_los_estados(client, estado):
    user = get_user_model().objects.create_user(username=f"convenio-{estado}")
    actividad = ActividadComercial.objects.create(nombre=f"Actividad {estado}")
    comercio = Comercio.objects.create(
        nombre=f"Comercio {estado}",
        actividad_comercial=actividad,
        usuario=user,
        estado=estado,
    )
    client.force_login(user)

    response = client.get(reverse("comercios:mi_convenio"))

    assert response.status_code == 200
    assert comercio.get_estado_display() in response.content.decode()


@pytest.mark.django_db
def test_mi_convenio_muestra_opcionales_sin_informar(client):
    user = get_user_model().objects.create_user(username="convenio-incompleto")
    actividad = ActividadComercial.objects.create(nombre="Actividad incompleta")
    Comercio.objects.create(
        nombre="Comercio incompleto",
        actividad_comercial=actividad,
        usuario=user,
    )
    client.force_login(user)

    response = client.get(reverse("comercios:mi_convenio"))

    assert response.status_code == 200
    assert response.content.decode().count("Sin informar") >= 7


@pytest.mark.django_db
def test_mi_convenio_redirige_si_el_rol_comercio_no_tiene_vinculo(client):
    user = get_user_model().objects.create_user(username="comercio-sin-vinculo")
    user.groups.add(Group.objects.get(name=COMERCIO_GROUP))
    client.force_login(user)

    response = client.get(reverse("comercios:mi_convenio"))

    assert response.status_code == 302
    assert response.url == reverse("web:home")


@pytest.mark.django_db
def test_mi_convenio_rechaza_usuario_sin_experiencia_comercio(client):
    user = get_user_model().objects.create_user(username="sin-comercio")
    client.force_login(user)

    response = client.get(reverse("comercios:mi_convenio"))

    assert response.status_code == 403
