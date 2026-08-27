from dataclasses import dataclass


@dataclass(frozen=True)
class EmailType:
    label: str
    subject: str
    template_base: str


EMAIL_TYPES = {
    "preinscripcion_recibida": EmailType(
        label="Preinscripción recibida",
        subject="Recibimos tu preinscripción en UNI2",
        template_base="comunicaciones/email/preinscripcion_recibida",
    ),
    "preinscripcion_correcciones_recibidas": EmailType(
        label="Correcciones recibidas",
        subject="Recibimos las correcciones de tu preinscripción",
        template_base="comunicaciones/email/preinscripcion_correcciones_recibidas",
    ),
    "preinscripcion_observada": EmailType(
        label="Solicitud observada",
        subject="Necesitamos que corrijas tu preinscripción",
        template_base="comunicaciones/email/preinscripcion_observada",
    ),
    "preinscripcion_datos_aprobados": EmailType(
        label="Documentación aprobada",
        subject="La documentación de tu preinscripción fue aprobada",
        template_base="comunicaciones/email/preinscripcion_datos_aprobados",
    ),
    "preinscripcion_cancelada": EmailType(
        label="Solicitud cancelada",
        subject="Tu solicitud de preinscripción fue cancelada",
        template_base="comunicaciones/email/preinscripcion_cancelada",
    ),
}
