import uuid
from datetime import date

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from asociados.models import Asociado, CicloLectivo
from asociados.services import create_asociado
from comercios.models import ActividadComercial, Comercio
from cuotas.models import Cuota, PeriodoCuota


def crear_asociado(*, dni, nombre="Ana", apellido="Pérez"):
    return create_asociado(
        nombre=nombre,
        apellido=apellido,
        dni=dni,
        tipo=Asociado.TIPO_ASOCIADO,
        fecha_alta="2026-08-01",
    )


def crear_comercio(*, estado=Comercio.ESTADO_FIRMADO):
    user = get_user_model().objects.create_user(username=f"comercio-{estado}", password="secreto123")
    actividad = ActividadComercial.objects.create(nombre=f"Actividad {estado}")
    comercio = Comercio.objects.create(
        nombre=f"Comercio {estado}",
        actividad_comercial=actividad,
        usuario=user,
        estado=estado,
    )
    return user, comercio


def url_credencial(asociado):
    return reverse("usuarios:resolver_credencial", kwargs={"token": asociado.token_credencial})


@pytest.mark.django_db
def test_ruta_de_credencial_es_neutral_y_usa_uuid():
    asociado = crear_asociado(dni="40111001")

    assert url_credencial(asociado) == f"/credenciales/{asociado.token_credencial}/"


@pytest.mark.django_db
def test_persona_anonima_inicia_sesion_y_regresa_a_la_url(client):
    asociado = crear_asociado(dni="40111002")
    destino = url_credencial(asociado)

    response = client.get(destino)
    assert response.status_code == 302
    assert response.url == f"{reverse('usuarios:login')}?next={destino}"

    response = client.post(
        f"{reverse('usuarios:login')}?next={destino}",
        {"username": asociado.usuario.username, "password": asociado.dni},
    )
    assert response.status_code == 302
    assert response.url == destino


@pytest.mark.django_db
def test_asociado_solo_abre_su_propia_credencial(client):
    asociado = crear_asociado(dni="40111003")
    otro = crear_asociado(dni="40111004", nombre="Nombre", apellido="Ajeno")
    client.force_login(asociado.usuario)

    propia = client.get(url_credencial(asociado))
    ajena = client.get(url_credencial(otro))

    assert propia.status_code == 302
    assert propia.url == reverse("asociados:credencial")
    assert ajena.status_code == 404
    assert "Nombre Ajeno" not in ajena.content.decode()
    assert str(otro.token_credencial) not in ajena.content.decode()


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("estado_asociado", "texto_esperado"),
    [
        (Asociado.ESTADO_ACTIVO, "Credencial activa"),
        (Asociado.ESTADO_INACTIVO, "Credencial inactiva"),
    ],
)
def test_comercio_firmado_valida_el_estado_actual(client, estado_asociado, texto_esperado):
    asociado = crear_asociado(dni=f"40112{estado_asociado == Asociado.ESTADO_ACTIVO}01")
    asociado.estado = estado_asociado
    asociado.save(update_fields=["estado"])
    user, _ = crear_comercio()
    client.force_login(user)

    response = client.get(url_credencial(asociado))

    assert response.status_code == 200
    assert texto_esperado in response.content.decode()
    assert asociado.nombre in response.content.decode()
    assert asociado.dni not in response.content.decode()


@pytest.mark.django_db
def test_comercio_no_ve_causa_ni_importes_de_una_credencial_inactiva_por_deuda(client, monkeypatch):
    monkeypatch.setattr("cuotas.selectors.timezone.localdate", lambda: date(2026, 8, 11))
    asociado = crear_asociado(dni="40111010")
    ciclo = CicloLectivo.objects.create(anio=2026)
    periodo = PeriodoCuota.objects.create(
        mes=8,
        ciclo_lectivo=ciclo,
        importe="1234.00",
        importe_recargo_mes="0.00",
        importe_recargo_mes_siguiente="0.00",
        fecha_vencimiento=date(2026, 8, 10),
    )
    Cuota.objects.create(asociado=asociado, periodo=periodo, importe="1234.00")
    user, _ = crear_comercio()
    client.force_login(user)

    content = client.get(url_credencial(asociado)).content.decode()

    assert "Credencial inactiva" in content
    assert asociado.nombre in content
    assert asociado.dni not in content
    assert "deuda" not in content.lower()
    assert "cuota" not in content.lower()
    assert "1.234" not in content


@pytest.mark.django_db
def test_comercio_sin_convenio_firmado_no_valida(client):
    asociado = crear_asociado(dni="40111007")
    user, _ = crear_comercio(estado=Comercio.ESTADO_PENDIENTE)
    client.force_login(user)

    response = client.get(url_credencial(asociado))

    assert response.status_code == 403
    assert "convenio firmado" in response.content.decode()
    assert asociado.nombre not in response.content.decode()


@pytest.mark.django_db
def test_rol_no_admitido_recibe_acceso_denegado(client):
    asociado = crear_asociado(dni="40111008")
    user = get_user_model().objects.create_user(username="sin-rol")
    client.force_login(user)

    response = client.get(url_credencial(asociado))

    assert response.status_code == 403
    assert asociado.nombre not in response.content.decode()


@pytest.mark.django_db
def test_uuid_inexistente_no_revela_datos(client):
    user, _ = crear_comercio()
    client.force_login(user)

    response = client.get(
        reverse("usuarios:resolver_credencial", kwargs={"token": uuid.uuid4()})
    )

    assert response.status_code == 200
    assert "Credencial inválida" in response.content.decode()
    assert "Nombre:" not in response.content.decode()


@pytest.mark.django_db
def test_token_con_formato_invalido_responde_404_generico(client):
    user = get_user_model().objects.create_user(username="formato-invalido")
    client.force_login(user)

    response = client.get("/credenciales/no-es-un-uuid/")

    assert response.status_code == 404
    assert response.headers["Referrer-Policy"] == "same-origin"


@pytest.mark.django_db
def test_respuesta_de_credencial_es_privada_y_no_envia_referente(client):
    asociado = crear_asociado(dni="40111009")
    client.force_login(asociado.usuario)

    response = client.get(url_credencial(asociado))

    assert "private" in response.headers["Cache-Control"]
    assert "no-store" in response.headers["Cache-Control"]
    assert response.headers["Referrer-Policy"] == "same-origin"
