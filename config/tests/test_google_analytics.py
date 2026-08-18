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
def test_analytics_expone_el_nombre_estable_de_la_vista_en_produccion():
    context = analytics_context(request_for("/productos-servicios/15/"))

    assert context == {
        "google_analytics_measurement_id": MEASUREMENT_ID,
        "google_analytics_page_name": "web:producto_servicio_detalle",
    }


@override_settings(
    UNI2_DEPLOYMENT_ENVIRONMENT="production",
    GOOGLE_ANALYTICS_MEASUREMENT_ID=MEASUREMENT_ID,
)
def test_analytics_no_expone_el_uuid_de_una_credencial():
    token = "123e4567-e89b-12d3-a456-426614174000"

    context = analytics_context(request_for(f"/credenciales/{token}/"))

    assert context["google_analytics_page_name"] == "usuarios:resolver_credencial"
    assert token not in str(context)


@pytest.mark.parametrize("environment", ["development", "staging"])
def test_analytics_permanece_deshabilitado_fuera_de_produccion(environment):
    with override_settings(
        UNI2_DEPLOYMENT_ENVIRONMENT=environment,
        GOOGLE_ANALYTICS_MEASUREMENT_ID=MEASUREMENT_ID,
    ):
        context = analytics_context(request_for("/"))

    assert context == {
        "google_analytics_measurement_id": "",
        "google_analytics_page_name": "",
    }


@pytest.mark.parametrize("measurement_id", ["", "UA-123", "G-invalid", "G-123 456"])
@override_settings(UNI2_DEPLOYMENT_ENVIRONMENT="production")
def test_analytics_rechaza_identificadores_vacios_o_invalidos(measurement_id):
    with override_settings(GOOGLE_ANALYTICS_MEASUREMENT_ID=measurement_id):
        context = analytics_context(request_for("/"))

    assert context == {
        "google_analytics_measurement_id": "",
        "google_analytics_page_name": "",
    }
