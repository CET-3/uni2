from .models import EntregaComunicacion


def listar_entregas_para_origen(entidad: str, objeto_id: object):
    return EntregaComunicacion.objects.filter(
        comunicacion__origen_entidad=entidad,
        comunicacion__origen_id=str(objeto_id),
    ).select_related("comunicacion")
