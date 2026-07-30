from io import BytesIO

from openpyxl import Workbook
from openpyxl.drawing.image import Image as SpreadsheetImage
from PIL import Image as PillowImage


COMERCIOS_HEADERS = [
    "COMERCIO",
    "CÓDIGO",
    "ACTIVIDAD COMERCIAL",
    "DESCUENTO",
    "INSTAGRAM",
    "UBICACIÓN",
    "DESCRIPCIÓN",
    "LOGO",
]


def build_comercios_xlsx(rows, *, image_rows=(), headers=COMERCIOS_HEADERS):
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Hoja 1"
    worksheet.append(headers)

    for row in rows:
        worksheet.append([row.get(header, "") for header in headers])

    image_streams = []
    for row_number in image_rows:
        image_stream = BytesIO()
        PillowImage.new("RGB", (20, 20), color=(20, 90, 160)).save(image_stream, format="PNG")
        image_stream.seek(0)
        image_streams.append(image_stream)
        worksheet.add_image(SpreadsheetImage(image_stream), f"H{row_number}")

    output = BytesIO()
    workbook.save(output)
    output.seek(0)
    return output
