from asociados.models import Asociado

from .models import Comercio


def validar_credencial(*, comercio: Comercio, token):
    if comercio.estado != Comercio.ESTADO_FIRMADO:
        raise ValueError("El comercio no tiene un convenio firmado.")

    asociado = Asociado.objects.filter(token_credencial=token).first()
    if asociado is None:
        return {"valida": False, "mensaje": "Credencial invalida"}

    return {
        "valida": asociado.estado == Asociado.ESTADO_ACTIVO,
        "nombre": asociado.nombre,
        "apellido": asociado.apellido,
        "tipo": asociado.tipo,
        "estado": asociado.estado,
    }
