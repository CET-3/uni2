import pytest
from django.test import RequestFactory, override_settings
from django.urls import resolve


MEASUREMENT_ID = "G-TEST123"


def analytics_context(request):
    from config.context_processors import google_analytics

    return google_analytics(request)


def request_for(path):
    request = RequestFactory().get(path)
    request.resolver_match = resolve(path)
    return request


@override_settings(
    UNI2_DEPLOYMENT_ENVIRONMENT="production",
    GOOGLE_ANALYTICS_MEASUREMENT_ID=MEASUREMENT_ID,
)
def test_analytics_expone_solo_el_identificador_en_produccion():
    context = analytics_context(request_for("/productos-servicios/15/"))

    assert context == {
        "google_analytics_measurement_id": MEASUREMENT_ID,
    }


@override_settings(
    UNI2_DEPLOYMENT_ENVIRONMENT="production",
    GOOGLE_ANALYTICS_MEASUREMENT_ID=MEASUREMENT_ID,
)
def test_analytics_no_normaliza_una_ruta_privada_en_el_contexto():
    token = "123e4567-e89b-12d3-a456-426614174000"

    context = analytics_context(request_for(f"/credenciales/{token}/"))

    assert context == {"google_analytics_measurement_id": MEASUREMENT_ID}


@pytest.mark.parametrize("environment", ["development", "staging"])
def test_analytics_permanece_deshabilitado_fuera_de_produccion(environment):
    with override_settings(
        UNI2_DEPLOYMENT_ENVIRONMENT=environment,
        GOOGLE_ANALYTICS_MEASUREMENT_ID=MEASUREMENT_ID,
    ):
        context = analytics_context(request_for("/"))

    assert context == {
        "google_analytics_measurement_id": "",
    }


@pytest.mark.parametrize("measurement_id", ["", "UA-123", "G-invalid", "G-123 456"])
@override_settings(UNI2_DEPLOYMENT_ENVIRONMENT="production")
def test_analytics_rechaza_identificadores_vacios_o_invalidos(measurement_id):
    with override_settings(GOOGLE_ANALYTICS_MEASUREMENT_ID=measurement_id):
        context = analytics_context(request_for("/"))

    assert context == {
        "google_analytics_measurement_id": "",
    }


@pytest.mark.django_db
@override_settings(
    UNI2_DEPLOYMENT_ENVIRONMENT="production",
    GOOGLE_ANALYTICS_MEASUREMENT_ID=MEASUREMENT_ID,
)
def test_base_carga_google_tag_con_la_configuracion_estandar(client):
    content = client.get("/").content.decode()

    assert (
        'src="https://www.googletagmanager.com/gtag/js?id=G-TEST123"'
        in content
    )
    assert 'id="uni2-google-analytics-config"' in content
    assert 'gtag("config", "G\\u002DTEST123");' in content
    assert 'gtag("event", "page_view"' not in content
    assert "send_page_view" not in content
    assert "page_title" not in content
    assert "page_location" not in content
    assert "page_referrer" not in content
    assert "/__analytics__/" not in content


@pytest.mark.django_db
@pytest.mark.parametrize("environment", ["development", "staging"])
def test_base_no_carga_google_tag_fuera_de_produccion(client, environment):
    with override_settings(
        UNI2_DEPLOYMENT_ENVIRONMENT=environment,
        GOOGLE_ANALYTICS_MEASUREMENT_ID=MEASUREMENT_ID,
    ):
        content = client.get("/").content.decode()

    assert "googletagmanager.com/gtag/js" not in content
    assert "uni2-google-analytics-config" not in content
