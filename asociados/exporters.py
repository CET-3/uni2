from __future__ import annotations

from io import BytesIO


ASOCIADOS_FORMATO_UNI2_HEADERS = [
    "numero_asociado",
    "apellido",
    "nombre",
    "dni",
    "tipo",
    "clasificacion_adherente",
    "email",
    "telefono",
    "direccion",
    "curso_anio",
    "curso_division",
    "division",
    "turno",
    "curso_nombre",
    "fecha_alta",
    "fecha_inicio_cobro",
    "estado",
    "motivo_baja",
]


def _date_to_text(value):
    if not value:
        return ""
    return value.isoformat()


def _curso_data(asociado):
    curso = asociado.curso_actual
    if not curso:
        return {
            "curso_anio": "",
            "curso_division": "",
            "division": "",
            "turno": "",
            "curso_nombre": "",
        }
    return {
        "curso_anio": curso.anio,
        "curso_division": curso.curso,
        "division": curso.division,
        "turno": curso.turno,
        "curso_nombre": f"{curso.anio} {curso.curso} {curso.division} {curso.turno}",
    }


def build_asociados_formato_uni2_xlsx(asociados):
    try:
        from openpyxl import Workbook
    except ImportError as exc:
        raise RuntimeError("Para exportar planillas .xlsx hace falta instalar openpyxl.") from exc

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "ASOCIADOS"
    worksheet.append(ASOCIADOS_FORMATO_UNI2_HEADERS)

    for asociado in asociados:
        curso = _curso_data(asociado)
        worksheet.append(
            [
                asociado.numero_asociado or "",
                asociado.apellido,
                asociado.nombre,
                asociado.dni,
                asociado.tipo,
                asociado.clasificacion_adherente.nombre if asociado.clasificacion_adherente else "",
                asociado.email,
                asociado.telefono,
                asociado.direccion,
                curso["curso_anio"],
                curso["curso_division"],
                curso["division"],
                curso["turno"],
                curso["curso_nombre"],
                _date_to_text(asociado.fecha_alta),
                _date_to_text(asociado.fecha_inicio_cobro),
                asociado.estado,
                asociado.motivo_baja,
            ]
        )

    buffer = BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()
