import pytest
from django.core.exceptions import ValidationError

from asociados.validators import (
    normalizar_documento,
    validar_nombre_persona,
    validar_telefono,
)


@pytest.mark.parametrize(
    ("entrada", "esperado"),
    [
        ("48.123.456", "48123456"),
        (" ab-123 cd ", "AB123CD"),
        ("bo 12.345-a", "BO12345A"),
    ],
)
def test_normalizar_documento_admite_dni_y_documento_extranjero(entrada, esperado):
    assert normalizar_documento(entrada) == esperado


@pytest.mark.parametrize("entrada", ["1234", "A" * 21, "AB/123", "---"])
def test_normalizar_documento_rechaza_longitud_o_caracteres_invalidos(entrada):
    with pytest.raises(ValidationError):
        normalizar_documento(entrada)


@pytest.mark.parametrize("nombre", ["Ana María", "O'Connor", "María-José", "Ñancufil"])
def test_validar_nombre_persona_admite_letras_unicode_y_separadores(nombre):
    validar_nombre_persona(nombre)


@pytest.mark.parametrize("nombre", ["Ana3", "Ana@", "---", ""])
def test_validar_nombre_persona_rechaza_numeros_simbolos_y_vacios(nombre):
    with pytest.raises(ValidationError):
        validar_nombre_persona(nombre)


@pytest.mark.parametrize("telefono", ["299 555-0192", "+54 (299) 555-0192"])
def test_validar_telefono_admite_formato_humano(telefono):
    validar_telefono(telefono)


@pytest.mark.parametrize("telefono", ["1234567", "1" * 16, "299 CALL-ME"])
def test_validar_telefono_rechaza_cantidad_o_caracteres_invalidos(telefono):
    with pytest.raises(ValidationError):
        validar_telefono(telefono)
