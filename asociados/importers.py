from __future__ import annotations

import logging
import re
from io import BytesIO
from collections import Counter
from dataclasses import dataclass, field
from datetime import date
from typing import Any

from django.db import transaction

from .models import Asociado, Curso



PADRON_IMPORT_SESSION_KEY = "padron_import_preview"
PADRON_FECHA_INICIO_COBRO = date(2026, 3, 1)
PADRON_IMPORT_LOG_EVERY = 25
logger = logging.getLogger(__name__)

ROLE_MAP = {
    "docente": "docente",
    "docentes": "docente",
    "profesor": "docente",
    "profesora": "docente",
    "profe": "docente",
    "preceptor": "preceptor",
    "preceptora": "preceptor",
    "director": "directivo",
    "directora": "directivo",
    "vicedirector": "directivo",
    "vicedirectora": "directivo",
    "portera": "auxiliar",
    "portero": "auxiliar",
    "bibliotecaria": "biblioteca",
    "bibliotecario": "biblioteca",
    "padrino mutual": "padrino_mutual",
    "particular": "particular",
}

ORD_ANIO = {"1": "1ro", "2": "2do", "3": "3ro", "4": "4to", "5": "5to", "6": "6to", "7": "7mo"}
ORD_DIVISION = {"1": "1ra", "2": "2da", "3": "3ra", "4": "4ta", "5": "5ta", "6": "6ta", "7": "7ma"}
CURSO_ANIO_ORDER = {value: index for index, value in enumerate(ORD_ANIO.values(), start=1)}
CURSO_DIVISION_ORDER = {value: index for index, value in enumerate(ORD_DIVISION.values(), start=1)}
CURSO_CICLO_ORDER = {Curso.DIVISION_CB: 1, Curso.DIVISION_CS: 2}
CURSO_TURNO_ORDER = {Curso.TURNO_TM: 1, Curso.TURNO_TT: 2}

PADRON_HEADERS = [
    "Fila original",
    "Número de asociado",
    "Apellido/nombre",
    "Curso/división/Ciclo/turno",
    "CICLO",
    "Categoria (act./adh.)",
    "DNI",
    "Celular",
    "Mail",
    "Dirección",
    "Motivo de revisión",
]


@dataclass
class PadronPreview:
    importables: list[dict[str, Any]] = field(default_factory=list)
    revisar: list[dict[str, Any]] = field(default_factory=list)
    no_importar_count: int = 0
    cursos_a_crear: list[dict[str, str]] = field(default_factory=list)

    @property
    def summary(self):
        return {
            "importar": len(self.importables),
            "revisar": len(self.revisar),
            "no_importar": self.no_importar_count,
            "cursos_a_crear": len(self.cursos_a_crear),
        }

    def as_session_data(self):
        return {
            "summary": self.summary,
            "importables": self.importables,
            "revisar": self.revisar,
            "cursos_a_crear": self.cursos_a_crear,
        }

    @classmethod
    def from_session_data(cls, data):
        preview = cls(
            importables=data.get("importables", []),
            revisar=data.get("revisar", []),
            no_importar_count=data.get("summary", {}).get("no_importar", 0),
            cursos_a_crear=data.get("cursos_a_crear", []),
        )
        return preview


@dataclass
class PadronImportResult:
    creados: int = 0
    actualizados: int = 0
    cursos_creados: int = 0
    omitidos: int = 0
    errores: list[str] = field(default_factory=list)


def _clean_value(value):
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def _clean_dni(value):
    return re.sub(r"\D", "", _clean_value(value))


def _normalize_tipo(value):
    raw = _clean_value(value)
    text = (
        raw.lower()
        .strip()
        .replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
    )
    if text in {"activo", "acttivo"}:
        return Asociado.TIPO_ASOCIADO, ""
    if text in {"adherente", "adherete"}:
        return Asociado.TIPO_ADHERENTE, ""
    if not text:
        return "", "Falta tipo"
    return "", f'Tipo dudoso: "{raw}"'


def _split_name(value):
    parts = [part for part in re.split(r"\s+", _clean_value(value)) if part]
    if not parts:
        return "[completar]", "[completar]", "Falta nombre y apellido"
    if len(parts) == 1:
        return parts[0], "[completar]", "Nombre completado con [completar]"
    return parts[0], " ".join(parts[1:]), ""


def _normalize_course_text(raw):
    text = raw.lower().strip().replace("º", "°")
    text = text.replace("c.b", " cb ").replace("c.s", " cs ")
    text = text.replace("c,b", " cb ").replace("c,s", " cs ")
    text = text.replace(".", " ").replace(",", " ")
    text = re.sub(r"(?<=\d)(ro|do|to|ra|da|ta|ma)(?=\D|$)", "", text)
    text = text.replace("ciclo basico", " cb ").replace("ciclo básico", " cb ")
    text = text.replace("ciclo superior", " cs ")
    return re.sub(r"\s+", " ", text).strip()


def _detect_role(curso_raw):
    text = _normalize_course_text(curso_raw)
    for raw_role, normalized in ROLE_MAP.items():
        if raw_role in text:
            return normalized
    return ""


def _infer_cycle(raw, ciclo, first_number):
    combined = _normalize_course_text(f"{raw} {ciclo}")
    if " cs " in f" {combined} ":
        return Curso.DIVISION_CS, ""
    if " cb " in f" {combined} ":
        if first_number and int(first_number) >= 3:
            return Curso.DIVISION_CS, "Ciclo corregido a CS (CB no tiene 3ro ni 4to)"
        return Curso.DIVISION_CB, ""
    if first_number:
        division = Curso.DIVISION_CB if int(first_number) <= 3 else Curso.DIVISION_CS
        return division, "División inferida por año"
    return "", ""


def _normalize_course(raw_value, ciclo_value):
    raw = _clean_value(raw_value)
    ciclo = _clean_value(ciclo_value)
    if not raw:
        return {}, "Falta curso", ""

    role = _detect_role(raw)
    if role:
        return {}, f'Rol/cargo en lugar de curso: "{raw}"', role

    text = _normalize_course_text(raw)
    if not text or set(text) <= {"-"}:
        return {}, f'Curso dudoso: "{raw}"', ""

    nums = re.findall(r"[1-7]", text)
    first = nums[0] if nums else ""
    division, note = _infer_cycle(raw, ciclo, first)
    notes = [note] if note else []

    if len(nums) >= 2 and division:
        data = {
            "curso_anio": ORD_ANIO[nums[0]],
            "curso_division": ORD_DIVISION[nums[1]],
            "division": division,
            "turno": Curso.TURNO_TM,
        }
        data["curso"] = _format_curso(data)
        return data, "; ".join(notes), ""

    if len(nums) == 1 and division:
        data = {"curso_anio": ORD_ANIO[nums[0]], "curso_division": "", "division": division, "turno": ""}
        return data, "Falta división/comisión del curso", ""

    return {}, f'Curso dudoso: "{raw}"', ""


def _format_curso(data):
    return f"{data['curso_anio']} {data['curso_division']} {data['division']} {data['turno']}"


def _dedupe_observaciones(observaciones):
    return "; ".join(dict.fromkeys([item for item in observaciones if item]))


def analyze_padron_xlsx(file_obj) -> PadronPreview:
    try:
        from openpyxl import load_workbook
    except ImportError as exc:
        raise RuntimeError("Para importar planillas .xlsx hace falta instalar openpyxl.") from exc

    workbook = load_workbook(file_obj, data_only=True)
    if "PADRÓN GENERAL" not in workbook.sheetnames:
        raise ValueError('El archivo debe tener una hoja llamada "PADRÓN GENERAL".')

    worksheet = workbook["PADRÓN GENERAL"]
    raw_rows = []
    for row_number in range(2, worksheet.max_row + 1):
        row = {
            "fila_origen": row_number,
            "numero_asociado": _clean_value(worksheet.cell(row_number, 1).value),
            "apellido_nombre_original": _clean_value(worksheet.cell(row_number, 2).value),
            "curso_original": _clean_value(worksheet.cell(row_number, 3).value),
            "ciclo_original": _clean_value(worksheet.cell(row_number, 4).value),
            "tipo_original": _clean_value(worksheet.cell(row_number, 5).value),
            "dni": _clean_dni(worksheet.cell(row_number, 6).value),
            "telefono": _clean_value(worksheet.cell(row_number, 7).value),
            "email": _clean_value(worksheet.cell(row_number, 8).value),
            "direccion": _clean_value(worksheet.cell(row_number, 9).value),
        }
        row["tiene_datos_persona"] = bool(row["apellido_nombre_original"] or row["dni"])
        row["tiene_alguna_celda"] = any(
            row[key]
            for key in [
                "numero_asociado",
                "apellido_nombre_original",
                "curso_original",
                "ciclo_original",
                "tipo_original",
                "dni",
                "telefono",
                "email",
                "direccion",
            ]
        )
        if row["tiene_alguna_celda"]:
            raw_rows.append(row)

    person_rows = [row for row in raw_rows if row["tiene_datos_persona"]]
    dni_counts = Counter(row["dni"] for row in person_rows if row["dni"])

    dni_groups: dict[str, list[dict]] = {}
    for row in person_rows:
        if row["dni"]:
            dni_groups.setdefault(row["dni"], []).append(row)

    no_importar_filas: set[int] = set()
    dni_conflict_filas: set[int] = set()
    for dni, rows in dni_groups.items():
        if len(rows) <= 1:
            continue
        names = set(r["apellido_nombre_original"].lower().strip() for r in rows)
        if len(names) == 1:
            for r in sorted(rows, key=lambda r: r["fila_origen"])[1:]:
                no_importar_filas.add(r["fila_origen"])
        else:
            for r in rows:
                dni_conflict_filas.add(r["fila_origen"])

    preview = PadronPreview()
    for row in raw_rows:
        if row["fila_origen"] in no_importar_filas:
            preview.no_importar_count += 1
            continue
        normalized = _normalize_row(row, dni_counts, dni_conflict_filas)
        if normalized["estado_importacion"] == "IMPORTAR":
            preview.importables.append(normalized)
        elif normalized["estado_importacion"] == "REVISAR":
            preview.revisar.append(normalized)
        else:
            preview.no_importar_count += 1

    preview.cursos_a_crear = _get_cursos_a_crear(preview.importables)
    return preview


def _normalize_row(row, dni_counts, dni_conflict_filas=None):
    if dni_conflict_filas is None:
        dni_conflict_filas = set()
    observaciones = []
    apellido, nombre, name_note = _split_name(row["apellido_nombre_original"])
    if name_note:
        observaciones.append(name_note)

    tipo, tipo_note = _normalize_tipo(row["tipo_original"])
    if tipo_note:
        observaciones.append(tipo_note)

    course_data, course_note, rol = _normalize_course(row["curso_original"], row["ciclo_original"])
    if course_note:
        observaciones.extend([note.strip() for note in course_note.split(";") if note.strip()])
    if rol:
        observaciones.append(f"Rol deducido: {rol}")

    output = {
        "estado_importacion": "IMPORTAR",
        "numero_asociado": row["numero_asociado"],
        "apellido": apellido,
        "nombre": nombre,
        "dni": row["dni"],
        "tipo": tipo,
        "curso": course_data.get("curso", ""),
        "curso_anio": course_data.get("curso_anio", ""),
        "curso_division": course_data.get("curso_division", ""),
        "division": course_data.get("division", ""),
        "turno": course_data.get("turno", ""),
        "rol_deducido": rol,
        "telefono": row["telefono"],
        "email": row["email"],
        "direccion": row["direccion"],
        "fila_origen": row["fila_origen"],
        "apellido_nombre_original": row["apellido_nombre_original"],
        "curso_original": row["curso_original"],
        "ciclo_original": row["ciclo_original"],
        "tipo_original": row["tipo_original"],
    }

    if not row["tiene_datos_persona"]:
        output["estado_importacion"] = "NO IMPORTAR"
        output["observaciones"] = "Fila sin persona: solo número o datos no personales"
        return output

    blockers = []
    dni = row["dni"]
    if not dni:
        blockers.append("falta DNI")
    elif len(dni) < 7 or len(dni) > 8:
        blockers.append(f"DNI con longitud dudosa: {dni}")
    elif dni and row["fila_origen"] in dni_conflict_filas:
        blockers.append("DNI duplicado")
    elif Asociado.objects.filter(dni=dni).exists():
        observaciones.append("El DNI ya existe: se actualizará el asociado")

    numero = row["numero_asociado"]
    if numero and not numero.isdigit():
        observaciones.append(f"número de asociado inválido en planilla: {numero}")

    output["numero_asociado"] = numero if numero and numero.isdigit() else ""

    if not tipo:
        blockers.append("tipo dudoso")
    if tipo == Asociado.TIPO_ASOCIADO and not output["curso"]:
        blockers.append("curso incompleto o dudoso para asociado")

    if blockers:
        output["estado_importacion"] = "REVISAR"
        observaciones.extend(blockers)

    if not row["telefono"]:
        observaciones.append("Falta teléfono")
    if not row["email"]:
        observaciones.append("Falta email")
    if not row["direccion"]:
        observaciones.append("Falta dirección")

    output["observaciones"] = _dedupe_observaciones(observaciones)
    return output


def _get_cursos_a_crear(importables):
    keys = {
        (
            row["curso_anio"],
            row["curso_division"],
            row["division"],
            row["turno"],
        )
        for row in importables
        if row.get("curso")
    }
    existing = set(
        Curso.objects.filter(
            anio__in=[key[0] for key in keys],
            curso__in=[key[1] for key in keys],
            division__in=[key[2] for key in keys],
            turno__in=[key[3] for key in keys],
        ).values_list("anio", "curso", "division", "turno")
    )
    cursos = []
    for anio, curso, division, turno in sorted(keys, key=_curso_sort_key):
        if (anio, curso, division, turno) not in existing:
            cursos.append(
                {
                    "curso_anio": anio,
                    "curso_division": curso,
                    "division": division,
                    "turno": turno,
                    "curso": f"{anio} {curso} {division} {turno}",
                }
            )
    return cursos


def _curso_sort_key(key):
    anio, curso, division, turno = key
    return (
        CURSO_CICLO_ORDER.get(division, 99),
        CURSO_ANIO_ORDER.get(anio, 99),
        CURSO_DIVISION_ORDER.get(curso, 99),
        CURSO_TURNO_ORDER.get(turno, 99),
    )


def build_revisar_padron_xlsx(preview: PadronPreview) -> bytes:
    try:
        from openpyxl import Workbook
    except ImportError as exc:
        raise RuntimeError("Para descargar planillas .xlsx hace falta instalar openpyxl.") from exc

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "PADRÓN GENERAL"
    worksheet.append(PADRON_HEADERS)

    for row in preview.revisar:
        worksheet.append(
            [
                row.get("fila_origen", ""),
                row.get("numero_asociado", ""),
                row.get("apellido_nombre_original", ""),
                row.get("curso_original", ""),
                row.get("ciclo_original", ""),
                row.get("tipo_original", ""),
                row.get("dni", ""),
                row.get("telefono", ""),
                row.get("email", ""),
                row.get("direccion", ""),
                row.get("observaciones", ""),
            ]
        )

    output = BytesIO()
    workbook.save(output)
    return output.getvalue()


@transaction.atomic
def import_padron_preview(preview: PadronPreview, fecha_alta: date) -> PadronImportResult:
    result = PadronImportResult()
    cursos = {}
    total = len(preview.importables)
    logger.info("Importacion de padron inicial iniciada: %s filas importables.", total)
    for index, row in enumerate(preview.importables, start=1):
        curso = None
        if row.get("curso"):
            key = (row["curso_anio"], row["curso_division"], row["division"], row["turno"])
            if key not in cursos:
                curso, created = Curso.objects.get_or_create(
                    anio=row["curso_anio"],
                    curso=row["curso_division"],
                    division=row["division"],
                    turno=row["turno"],
                    defaults={"activo": True},
                )
                if created:
                    result.cursos_creados += 1
                cursos[key] = curso
            curso = cursos[key]

        try:
            _upsert_asociado(row, curso, fecha_alta, result)
        except Exception as exc:  # noqa: BLE001
            result.errores.append(f"Fila {row.get('fila_origen')}: {exc}")

        if index == total or index % PADRON_IMPORT_LOG_EVERY == 0:
            logger.info("Importacion de padron inicial: %s/%s filas procesadas.", index, total)

    result.omitidos = len(preview.revisar) + preview.no_importar_count
    logger.info(
        "Importacion de padron inicial finalizada: %s creados, %s actualizados, "
        "%s cursos creados, %s omitidos, %s errores.",
        result.creados,
        result.actualizados,
        result.cursos_creados,
        result.omitidos,
        len(result.errores),
    )
    return result


def _upsert_asociado(row, curso, fecha_alta, result):
    defaults = {
        "apellido": row["apellido"],
        "nombre": row["nombre"],
        "tipo": row["tipo"],
        "curso_actual": curso,
        "telefono": row.get("telefono", ""),
        "email": row.get("email", ""),
        "direccion": row.get("direccion", ""),
        "estado": Asociado.ESTADO_ACTIVO,
        "fecha_alta": fecha_alta,
        "fecha_inicio_cobro": PADRON_FECHA_INICIO_COBRO,
    }
    asociado, created = Asociado.objects.update_or_create(dni=row["dni"], defaults=defaults)
    if created:
        result.creados += 1
    else:
        result.actualizados += 1
    return asociado
