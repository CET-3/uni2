from django.utils import timezone

from asociados.models import Asociado

from .models import BeneficioComercio, Comercio


def validar_credencial(*, comercio: Comercio, token):
    if not comercio.activo:
        raise ValueError("El comercio esta inactivo.")

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


def beneficios_vigentes_para_comercio(comercio: Comercio):
    today = timezone.localdate()
    return BeneficioComercio.objects.filter(
        comercio=comercio,
        activo=True,
    ).filter(
        models.Q(fecha_desde__isnull=True) | models.Q(fecha_desde__lte=today),
        models.Q(fecha_hasta__isnull=True) | models.Q(fecha_hasta__gte=today),
    )

