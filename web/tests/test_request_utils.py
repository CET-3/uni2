from django.test import RequestFactory, override_settings

from web.request_utils import obtener_ip_cliente


@override_settings(UNI2_TRUST_VERCEL_CLIENT_IP=False)
def test_ip_cliente_local_usa_remote_addr_y_no_confia_en_forwarded_for():
    request = RequestFactory().get(
        "/",
        REMOTE_ADDR="203.0.113.10",
        HTTP_X_FORWARDED_FOR="198.51.100.20",
    )

    assert obtener_ip_cliente(request) == "203.0.113.10"


@override_settings(UNI2_TRUST_VERCEL_CLIENT_IP=True)
def test_ip_cliente_en_vercel_usa_su_encabezado_y_normaliza_ipv6():
    request = RequestFactory().get(
        "/",
        REMOTE_ADDR="127.0.0.1",
        HTTP_X_VERCEL_FORWARDED_FOR="2001:0db8::1, 10.0.0.1",
    )

    assert obtener_ip_cliente(request) == "2001:db8::1"


@override_settings(UNI2_TRUST_VERCEL_CLIENT_IP=True)
def test_ip_cliente_en_vercel_vuelve_a_remote_addr_si_el_encabezado_es_invalido():
    request = RequestFactory().get(
        "/",
        REMOTE_ADDR="203.0.113.10",
        HTTP_X_VERCEL_FORWARDED_FOR="valor-invalido",
    )

    assert obtener_ip_cliente(request) == "203.0.113.10"


@override_settings(UNI2_TRUST_VERCEL_CLIENT_IP=True)
def test_ip_cliente_no_confia_en_forwarded_for_generico():
    request = RequestFactory().get(
        "/",
        REMOTE_ADDR="203.0.113.10",
        HTTP_X_FORWARDED_FOR="198.51.100.20",
    )

    assert obtener_ip_cliente(request) == "203.0.113.10"
