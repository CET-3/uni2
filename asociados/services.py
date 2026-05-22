from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date

from django.db import transaction

from .models import Asociado, Curso, InscripcionCurso


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

    if curso_actual:
        InscripcionCurso.objects.create(
            asociado=asociado,
            curso=curso_actual,
            ciclo_lectivo=fecha_alta.year,
            activa=True,
            fecha_desde=fecha_alta,
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


@transaction.atomic
def cambiar_curso(asociado: Asociado, nuevo_curso: Curso, ciclo_lectivo: int, fecha_desde: date):
    asociado.inscripciones.filter(activa=True).update(activa=False, fecha_hasta=fecha_desde)
    inscripcion = InscripcionCurso.objects.create(
        asociado=asociado,
        curso=nuevo_curso,
        ciclo_lectivo=ciclo_lectivo,
        activa=True,
        fecha_desde=fecha_desde,
    )
    asociado.curso_actual = nuevo_curso
    asociado.save(update_fields=["curso_actual"])
    return inscripcion


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
            curso_nombre = (row.get("curso") or "").strip()
            if curso_nombre:
                curso = Curso.objects.filter(nombre=curso_nombre).first()
                if curso is None:
                    raise ValueError(f"Curso inexistente: {curso_nombre}")

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
