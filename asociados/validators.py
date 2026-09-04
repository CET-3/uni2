import re
import unicodedata

from django.core.exceptions import ValidationError


def normalizar_documento(valor: str) -> str:
    normalizado = re.sub(r"[.\s-]+", "", (valor or "")).upper()
    if not 5 <= len(normalizado) <= 20 or not normalizado.isalnum():
        raise ValidationError(
            "Ingresá un DNI o documento de entre 5 y 20 letras y números."
        )
    return normalizado


def validar_nombre_persona(valor: str) -> None:
    nombre = (valor or "").strip()
    caracteres_admitidos = {" ", "'", "’", "-"}
    if not nombre or not any(unicodedata.category(caracter).startswith("L") for caracter in nombre):
        raise ValidationError("Ingresá un nombre válido.")
    if any(
        not unicodedata.category(caracter).startswith("L")
        and caracter not in caracteres_admitidos
        for caracter in nombre
    ):
        raise ValidationError("Usá solamente letras, espacios, apóstrofes y guiones.")


def validar_telefono(valor: str) -> None:
    telefono = valor or ""
    if not re.fullmatch(r"[0-9+()\-\s]+", telefono):
        raise ValidationError("Ingresá un teléfono válido.")
    cantidad_digitos = sum(caracter.isdigit() for caracter in telefono)
    if not 8 <= cantidad_digitos <= 15:
        raise ValidationError("El teléfono debe contener entre 8 y 15 números.")
