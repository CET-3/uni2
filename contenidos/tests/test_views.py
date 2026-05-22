import pytest
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    "url_name",
    [
        "contenidos:home",
        "contenidos:beneficios",
        "contenidos:servicios",
        "contenidos:horarios",
        "contenidos:comercios",
    ],
)
def test_paginas_publicas_responden(client, url_name):
    response = client.get(reverse(url_name))
    assert response.status_code == 200

