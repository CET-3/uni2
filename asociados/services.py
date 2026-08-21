from __future__ import annotations

import csv
import uuid
from dataclasses import dataclass
from datetime import date

from django.db import transaction

from auditoria.models import EventoAuditoria
from auditoria.services import construir_cambios, registrar_evento
from usuarios.services import create_user_for_asociado, ensure_default_groups

from .models import Asociado, ClasificacionAdherente, Curso


CAMPOS_AUDITABLES_ASOCIADO = (
    "nombre",
    "apellido",
    "dni",
    "email",
    "telefono",
    "direccion",
    "tipo",
    "curso_actual",
    "clasificacion_adherente",
    "estado",
    "fecha_alta",
    "fecha_inicio_cobro",
    "fecha_baja",
    "motivo_baja",
)


def _valores_auditables_asociado(asociado):
    return {campo: getattr(asociado, campo) for campo in CAMPOS_AUDITABLES_ASOCIADO}


def calculate_fecha_inicio_cobro(fecha_alta: date) -> date:
    if fecha_alta.day <= 15:
        return fecha_alta.replace(day=1)

    if fecha_alta.month == 12:
        return date(fecha_alta.year + 1, 1, 1)
    return date(fecha_alta.year, fecha_alta.month + 1, 1)


@transaction.atomic
def create_asociado(
    *,
    nombre: str,
    apellido: str,
    dni: str,
    tipo: str,
    fecha_alta: date | str,
    curso_actual: Curso | None = None,
    clasificacion_adherente=None,
    fecha_inicio_cobro: date | str | None = None,
    email: str = "",
    telefono: str = "",
    direccion: str = "",
    actor=None,
    origen: str = EventoAuditoria.ORIGEN_GESTION,
):
    operacion_id = uuid.uuid4()
    if isinstance(fecha_alta, str):
        fecha_alta = date.fromisoformat(fecha_alta)
    if isinstance(fecha_inicio_cobro, str):
        fecha_inicio_cobro = date.fromisoformat(fecha_inicio_cobro)

    if Asociado.objects.filter(dni=dni).exists():
        raise ValueError("Ya existe un asociado con ese DNI.")

    fecha_inicio = fecha_inicio_cobro or calculate_fecha_inicio_cobro(fecha_alta)
    if tipo == Asociado.TIPO_ASOCIADO:
        clasificacion_adherente = None
    else:
        curso_actual = None
        if clasificacion_adherente is None:
            clasificacion_adherente = ClasificacionAdherente.objects.get(
                nombre=ClasificacionAdherente.NOMBRE_SIN_CLASIFICAR
            )
    asociado = Asociado.objects.create(
        nombre=nombre,
        apellido=apellido,
        dni=dni,
        tipo=tipo,
        curso_actual=curso_actual,
        clasificacion_adherente=clasificacion_adherente,
        fecha_alta=fecha_alta,
        fecha_inicio_cobro=fecha_inicio,
        email=email,
        telefono=telefono,
        direccion=direccion,
    )

    ensure_default_groups()
    create_user_for_asociado(
        asociado=asociado,
        password=dni,
        actor=actor,
        operacion_id=operacion_id,
    )

    if actor is not None:
        nuevos = _valores_auditables_asociado(asociado)
        registrar_evento(
            actor=actor,
            accion=EventoAuditoria.ACCION_CREAR,
            entidad="asociados.Asociado",
            objeto_id=asociado.pk,
            objeto_descripcion=str(asociado),
            cambios=construir_cambios(
                anteriores={campo: None for campo in CAMPOS_AUDITABLES_ASOCIADO},
                nuevos=nuevos,
                campos=CAMPOS_AUDITABLES_ASOCIADO,
            ),
            origen=origen,
            operacion_id=operacion_id,
        )

    return asociado


@transaction.atomic
def actualizar_asociado(*, asociado: Asociado, datos, campos_modificados, actor):
    campos = [campo for campo in campos_modificados if campo in CAMPOS_AUDITABLES_ASOCIADO]
    if not campos:
        return asociado

    asociado_anterior = Asociado.objects.select_related("curso_actual").get(pk=asociado.pk)
    anteriores = _valores_auditables_asociado(asociado_anterior)
    for campo in campos:
        setattr(asociado, campo, datos[campo])
    asociado.save(update_fields=campos)
    nuevos = _valores_auditables_asociado(asociado)
    cambios = construir_cambios(anteriores=anteriores, nuevos=nuevos, campos=campos)
    if cambios:
        registrar_evento(
            actor=actor,
            accion=EventoAuditoria.ACCION_MODIFICAR,
            entidad="asociados.Asociado",
            objeto_id=asociado.pk,
            objeto_descripcion=str(asociado),
            cambios=cambios,
            origen=EventoAuditoria.ORIGEN_GESTION,
        )
    return asociado


@transaction.atomic
def dar_baja_asociado(
    asociado: Asociado,
    fecha_baja: date,
    motivo_baja: str,
    *,
    actor=None,
):
    anteriores = {
        "estado": asociado.estado,
        "fecha_baja": asociado.fecha_baja,
        "motivo_baja": asociado.motivo_baja,
    }
    asociado.estado = Asociado.ESTADO_INACTIVO
    asociado.fecha_baja = fecha_baja
    asociado.motivo_baja = motivo_baja
    asociado.save(update_fields=["estado", "fecha_baja", "motivo_baja"])
    registrar_evento(
        actor=actor,
        actor_etiqueta="Sistema: baja de asociado",
        accion=EventoAuditoria.ACCION_CAMBIAR_ESTADO,
        entidad=asociado._meta.label,
        objeto_id=asociado.pk,
        objeto_descripcion=str(asociado),
        cambios=construir_cambios(
            anteriores=anteriores,
            nuevos={
                "estado": asociado.estado,
                "fecha_baja": asociado.fecha_baja,
                "motivo_baja": asociado.motivo_baja,
            },
            campos=("estado", "fecha_baja", "motivo_baja"),
        ),
        motivo=motivo_baja,
        origen=EventoAuditoria.ORIGEN_GESTION if actor else EventoAuditoria.ORIGEN_SISTEMA,
    )
    return asociado


@dataclass
class ImportResult:
    created: int = 0
    errors: list[str] | None = None

    def __post_init__(self):
        self.errors = self.errors or []


def import_asociados_from_csv(csv_file) -> ImportResult:
    result = ImportResult()
    reader = csv.DictReader(csv_file)
    for index, row in enumerate(reader, start=2):
        try:
            curso = None
            curso_str = (row.get("curso") or "").strip()
            if curso_str:
                partes = curso_str.split()
                filtro = {}
                if len(partes) >= 1:
                    filtro["anio"] = partes[0]
                if len(partes) >= 2:
                    filtro["curso"] = partes[1]
                if len(partes) >= 3:
                    filtro["division"] = partes[2]
                if len(partes) >= 4:
                    filtro["turno"] = partes[3]
                curso = Curso.objects.filter(**filtro).first()
                if curso is None:
                    raise ValueError(f"Curso inexistente: {curso_str}")

            create_asociado(
                nombre=row["nombre"].strip(),
                apellido=row["apellido"].strip(),
                dni=row["dni"].strip(),
                tipo=row["tipo"].strip(),
                fecha_alta=row["fecha_alta"].strip(),
                curso_actual=curso,
                email=(row.get("email") or "").strip(),
                telefono=(row.get("telefono") or "").strip(),
            )
            result.created += 1
        except Exception as exc:  # noqa: BLE001
            result.errors.append(f"Fila {index}: {exc}")
    return result
