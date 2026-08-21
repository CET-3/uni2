from dataclasses import dataclass

from django.urls import reverse

from gestion.permissions import (
    GESTION_ADMINISTRAR_PERIODOS_CUOTA,
    GESTION_IMPORTAR_ASOCIADOS,
    GESTION_IMPORTAR_CUOTAS_HISTORICAS,
    GESTION_CONSULTAR_ASOCIADOS,
    GESTION_VER_AUDITORIA,
    GESTION_VER_DESIGN_SYSTEM,
    GESTION_VER_ESPECIFICACION,
)

from .roles import ACCESO_ADMIN_TECNICO
from .services import get_available_experiences


PERFIL_ASOCIADO = "asociado"
PERFIL_COMERCIO = "comercio"
PERFIL_GESTION = "gestion"
PERFILES_DISPONIBLES = (PERFIL_ASOCIADO, PERFIL_COMERCIO, PERFIL_GESTION)


@dataclass(frozen=True)
class HomeAction:
    label: str
    url: str
    description: str = ""


def _acciones_selector(experiencias):
    definiciones = {
        PERFIL_ASOCIADO: (
            "Mi cuenta de asociado",
            "Credencial, cuotas y beneficios.",
        ),
        PERFIL_COMERCIO: (
            "Mi comercio",
            "Validación de credenciales.",
        ),
        PERFIL_GESTION: (
            "Administración",
            "Tareas autorizadas de la mutual.",
        ),
    }
    home_url = reverse("web:home")
    return [
        HomeAction(
            label=definiciones[experiencia][0],
            url=f"{home_url}?perfil={experiencia}",
            description=definiciones[experiencia][1],
        )
        for experiencia in PERFILES_DISPONIBLES
        if experiencia in experiencias
    ]


def _acciones_gestion(user):
    definiciones = (
        (
            GESTION_CONSULTAR_ASOCIADOS,
            "Atención al asociado",
            "gestion:asociados",
            "Buscar asociados, revisar sus datos y operar sobre su cuenta.",
        ),
        (
            GESTION_ADMINISTRAR_PERIODOS_CUOTA,
            "Períodos de cuota",
            "gestion:periodos_cuota",
            "Crear períodos y generar cuotas.",
        ),
        (
            GESTION_VER_AUDITORIA,
            "Auditoría",
            "gestion:auditoria",
            "Revisar operaciones registradas por Uni2.",
        ),
        (
            GESTION_IMPORTAR_ASOCIADOS,
            "Importar padrón inicial",
            "gestion:importar_asociados",
            "Cargar asociados desde la planilla heredada.",
        ),
        (
            GESTION_IMPORTAR_CUOTAS_HISTORICAS,
            "Importar cuotas históricas",
            "gestion:importar_cuotas_historicas",
            "Cargar cuotas y pagos históricos.",
        ),
        (
            GESTION_VER_ESPECIFICACION,
            "Especificación",
            "especificacion:indice",
            "Consultar la documentación funcional y técnica.",
        ),
        (
            GESTION_VER_DESIGN_SYSTEM,
            "Design system",
            "web:design-system",
            "Consultar los componentes visuales de Uni2.",
        ),
    )
    acciones = [
        HomeAction(label=label, url=reverse(url_name), description=description)
        for permission, label, url_name, description in definiciones
        if user.has_perm(permission)
    ]
    if user.has_perm(ACCESO_ADMIN_TECNICO):
        acciones.append(
            HomeAction(
                label="Admin técnico",
                url=reverse("admin:index"),
                description="Administrar las áreas técnicas habilitadas para tu usuario.",
            )
        )
    return acciones


def _presentacion_perfil(user, perfil):
    if perfil == PERFIL_ASOCIADO:
        asociado = user.asociado
        return {
            "variant": PERFIL_ASOCIADO,
            "eyebrow": "Mi panel",
            "title": f"Hola, {asociado.nombre}.",
            "subtitle": "Desde acá podés entrar a las pantallas principales de asociado.",
            "actions": [
                HomeAction("Mi credencial", reverse("asociados:credencial")),
                HomeAction("Mis cuotas", reverse("asociados:cuotas")),
            ],
        }
    if perfil == PERFIL_COMERCIO:
        comercio = user.comercio
        return {
            "variant": PERFIL_COMERCIO,
            "eyebrow": "Mi comercio",
            "title": comercio.nombre,
            "subtitle": "Pantalla simple para validar credenciales de asociados.",
            "actions": [
                HomeAction("Validar credencial", reverse("comercios:validar_credencial")),
                HomeAction("Mi convenio", reverse("comercios:mi_convenio")),
            ],
        }
    return {
        "variant": PERFIL_GESTION,
        "eyebrow": "Administración interna",
        "title": "Panel de gestión",
        "subtitle": "Accesos directos a las tareas de la mutual habilitadas para tu usuario.",
        "actions": _acciones_gestion(user),
    }


def build_home_navigation(user, requested_profile=None):
    experiencias = get_available_experiences(user)

    if not user.is_authenticated or not experiencias:
        acciones = [HomeAction("Sumate", "#como-asociarse")]
        if not user.is_authenticated:
            acciones.append(HomeAction("Iniciar sesión", reverse("usuarios:login")))
        presentation = {
            "variant": "publica",
            "eyebrow": "Mutual Escolar UNI2",
            "title": "Tu mutual, más cerca que nunca",
            "subtitle": "Una comunidad comprometida con vos, con beneficios para cada momento",
            "actions": acciones,
        }
    elif len(experiencias) > 1 and requested_profile not in experiencias:
        presentation = {
            "variant": "multiperfil",
            "eyebrow": "Acceso",
            "title": "Elegí cómo querés ingresar",
            "subtitle": "Tu usuario tiene más de una experiencia disponible.",
            "actions": _acciones_selector(experiencias),
        }
    else:
        perfil = experiencias[0] if len(experiencias) == 1 else requested_profile
        presentation = _presentacion_perfil(user, perfil)

    acciones = presentation.pop("actions")
    presentation["primary_actions"] = acciones[:2]
    presentation["extra_actions"] = acciones[2:]
    presentation["available_experiences"] = experiencias
    return presentation
