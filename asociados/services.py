from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date

from django.db import transaction

from .models import Asociado, Curso


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
    fecha_inicio_cobro: date | str | None = None,
    email: str = "",
    telefono: str = "",
    fecha_nacimiento: date | None = None,
):
    if isinstance(fecha_alta, str):
        fecha_alta = date.fromisoformat(fecha_alta)
    if isinstance(fecha_inicio_cobro, str):
        fecha_inicio_cobro = date.fromisoformat(fecha_inicio_cobro)

    if Asociado.objects.filter(dni=dni).exists():
        raise ValueError("Ya existe un asociado con ese DNI.")

    fecha_inicio = fecha_inicio_cobro or calculate_fecha_inicio_cobro(fecha_alta)
    asociado = Asociado.objects.create(
        nombre=nombre,
        apellido=apellido,
        dni=dni,
        tipo=tipo,
        curso_actual=curso_actual,
        fecha_alta=fecha_alta,
        fecha_inicio_cobro=fecha_inicio,
        email=email,
        telefono=telefono,
        fecha_nacimiento=fecha_nacimiento,
    )

    return asociado


@transaction.atomic
def dar_baja_asociado(asociado: Asociado, fecha_baja: date, motivo_baja: str):
    asociado.estado = Asociado.ESTADO_INACTIVO
    asociado.fecha_baja = fecha_baja
    asociado.motivo_baja = motivo_baja
    asociado.save(update_fields=["estado", "fecha_baja", "motivo_baja"])
    return asociado


@transaction.atomic
def marcar_asociado_como_egresado(asociado: Asociado):
    asociado.estado = Asociado.ESTADO_EGRESADO
    asociado.save(update_fields=["estado"])
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
