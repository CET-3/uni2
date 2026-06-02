import pytest
from django.urls import reverse


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
