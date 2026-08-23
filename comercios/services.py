from asociados.selectors import get_asociado_by_credential_identifier
from cuotas.selectors import calcular_estado_credencial

from .models import Comercio


def validar_credencial(*, comercio: Comercio, token=None, identificador=None, fecha_referencia=None):
    if comercio.estado != Comercio.ESTADO_FIRMADO:
        raise ValueError("El comercio no tiene un convenio firmado.")

    asociado = get_asociado_by_credential_identifier(
        identificador if identificador is not None else token
    )
    if asociado is None:
        return {
            "encontrada": False,
            "valida": False,
            "mensaje": "Credencial inválida",
        }

    estado_credencial = calcular_estado_credencial(asociado, fecha_referencia)
    dato_etiqueta, dato_valor = asociado.get_dato_institucional()

    return {
        "encontrada": True,
        "valida": estado_credencial.activa,
        "nombre": asociado.nombre,
        "apellido": asociado.apellido,
        "dni": asociado.dni,
        "tipo": asociado.get_tipo_display(),
        "estado_credencial": estado_credencial.estado_display,
        "dato_institucional_etiqueta": dato_etiqueta,
        "dato_institucional_valor": dato_valor,
    }
