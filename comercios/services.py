from asociados.models import Asociado
from asociados.selectors import get_asociado_by_credential_token

from .models import Comercio


def validar_credencial(*, comercio: Comercio, token):
    if comercio.estado != Comercio.ESTADO_FIRMADO:
        raise ValueError("El comercio no tiene un convenio firmado.")

    asociado = get_asociado_by_credential_token(token)
    if asociado is None:
        return {"valida": False, "mensaje": "Credencial inválida"}

    return {
        "valida": asociado.estado == Asociado.ESTADO_ACTIVO,
        "nombre": asociado.nombre,
        "apellido": asociado.apellido,
        "tipo": asociado.tipo,
        "estado": asociado.estado,
    }
