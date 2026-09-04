import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.urls import reverse

from asociados.forms import AsociadoDatosPropiosForm
from asociados.models import Asociado
from asociados.services import (
    actualizar_datos_propios_asociado,
    create_asociado,
)
from auditoria.models import EventoAuditoria
from comunicaciones.models import Comunicacion


@pytest.fixture
def asociado(db):
    return create_asociado(
        nombre="Ana",
        apellido="Flores",
        dni="48123456",
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta="2026-09-04",
        email="anterior@example.com",
        telefono="2995550101",
        direccion="Los Maitenes 100",
    )


def datos_validos(**cambios):
    datos = {
        "nombre": "Ana María",
        "apellido": "Flores Díaz",
        "telefono": "+54 (299) 555-0192",
        "email": "nuevo@example.com",
        "direccion": "Los Maitenes 142",
    }
    datos.update(cambios)
    return datos


@pytest.mark.django_db
def test_asociado_actualiza_solo_datos_propios_y_sincroniza_usuario(
    asociado,
):
    actualizado = actualizar_datos_propios_asociado(
        asociado=asociado,
        actor=asociado.usuario,
        datos=datos_validos(),
    )

    actualizado.usuario.refresh_from_db()
    assert actualizado.nombre == "Ana María"
    assert actualizado.apellido == "Flores Díaz"
    assert actualizado.telefono == "+54 (299) 555-0192"
    assert actualizado.email == "nuevo@example.com"
    assert actualizado.direccion == "Los Maitenes 142"
    assert actualizado.usuario.first_name == "Ana María"
    assert actualizado.usuario.last_name == "Flores Díaz"
    assert actualizado.usuario.email == "nuevo@example.com"
    evento = EventoAuditoria.objects.get(
        entidad="asociados.Asociado",
        objeto_id=str(actualizado.pk),
    )
    assert evento.actor == asociado.usuario
    assert evento.origen == EventoAuditoria.ORIGEN_ASOCIADO
    assert set(evento.cambios) == {
        "nombre",
        "apellido",
        "telefono",
        "email",
        "direccion",
    }


def test_formulario_de_datos_propios_tiene_lista_cerrada_y_contacto_opcional():
    form = AsociadoDatosPropiosForm(
        data=datos_validos(telefono="", email="", direccion="")
    )

    assert tuple(form.fields) == (
        "nombre",
        "apellido",
        "telefono",
        "email",
        "direccion",
    )
    assert form.is_valid()


@pytest.mark.django_db
def test_formulario_precarga_los_datos_actuales(asociado):
    form = AsociadoDatosPropiosForm(instance=asociado)

    assert form.initial == {
        "nombre": "Ana",
        "apellido": "Flores",
        "telefono": "2995550101",
        "email": "anterior@example.com",
        "direccion": "Los Maitenes 100",
    }


@pytest.mark.parametrize(
    ("campo", "valor"),
    [
        ("nombre", ""),
        ("apellido", "Flores 2"),
        ("telefono", "teléfono inválido"),
        ("email", "correo-invalido"),
    ],
)
def test_formulario_rechaza_datos_personales_invalidos(campo, valor):
    form = AsociadoDatosPropiosForm(data=datos_validos(**{campo: valor}))

    assert not form.is_valid()
    assert campo in form.errors


@pytest.mark.django_db
def test_usuario_no_puede_modificar_otro_asociado(asociado):
    otro_usuario = get_user_model().objects.create_user(username="otro")

    with pytest.raises(PermissionDenied):
        actualizar_datos_propios_asociado(
            asociado=asociado,
            actor=otro_usuario,
            datos=datos_validos(),
        )

    asociado.refresh_from_db()
    assert asociado.nombre == "Ana"
    assert not EventoAuditoria.objects.exists()


@pytest.mark.django_db
def test_cambiar_o_agregar_email_no_programa_comunicaciones(asociado):
    actualizado = actualizar_datos_propios_asociado(
        asociado=asociado,
        actor=asociado.usuario,
        datos=datos_validos(email="agregado@example.com"),
    )

    assert actualizado.email == "agregado@example.com"
    assert not Comunicacion.objects.exists()


@pytest.mark.django_db
def test_post_manipulado_modifica_solamente_los_cinco_campos(
    client,
    asociado,
):
    numero_original = asociado.numero_asociado
    client.force_login(asociado.usuario)

    response = client.post(
        reverse("asociados:datos_propios"),
        {
            "nombre": "Ana",
            "apellido": "Actualizada",
            "telefono": "",
            "email": "",
            "direccion": "",
            "dni": "00000000",
            "tipo": Asociado.TIPO_ADHERENTE,
            "estado": Asociado.ESTADO_INACTIVO,
            "numero_asociado": 9999,
        },
        follow=True,
    )

    asociado.refresh_from_db()
    assert response.status_code == 200
    assert asociado.apellido == "Actualizada"
    assert asociado.dni == "48123456"
    assert asociado.tipo == Asociado.TIPO_ASOCIADO
    assert asociado.estado == Asociado.ESTADO_ACTIVO
    assert asociado.numero_asociado == numero_original
    assert "Tus datos se actualizaron correctamente" in response.content.decode()


@pytest.mark.django_db
def test_visitante_debe_ingresar_para_editar_datos_propios(client):
    url = reverse("asociados:datos_propios")

    response = client.get(url)

    assert response.status_code == 302
    assert response.url == f"{reverse('usuarios:login')}?next={url}"


@pytest.mark.django_db
def test_usuario_sin_asociado_no_puede_editar_datos_propios(client):
    usuario = get_user_model().objects.create_user(username="sin-asociado")
    client.force_login(usuario)

    response = client.get(reverse("asociados:datos_propios"))

    assert response.status_code == 403


@pytest.mark.django_db
def test_pantalla_muestra_cinco_campos_y_advierte_sobre_email(
    client,
    asociado,
):
    client.force_login(asociado.usuario)

    contenido = client.get(reverse("asociados:datos_propios")).content.decode()

    assert contenido.count('class="form-control"') == 5
    assert "Sin email no vas a poder recibir correos ni usar Olvidé mi contraseña" in contenido
    assert "Guardar cambios" in contenido
    assert "DNI" not in contenido


@pytest.mark.django_db
def test_navbar_ofrece_mis_datos_solamente_al_asociado(client, asociado):
    client.force_login(asociado.usuario)
    contenido_asociado = client.get(reverse("web:home")).content.decode()

    assert contenido_asociado.count(reverse("asociados:datos_propios")) == 2
    assert "Mis datos" in contenido_asociado

    otro_usuario = get_user_model().objects.create_user(username="otro-perfil")
    client.force_login(otro_usuario)
    contenido_otro = client.get(reverse("web:home")).content.decode()

    assert reverse("asociados:datos_propios") not in contenido_otro
    assert "Mis datos" not in contenido_otro
