import re
from itertools import groupby

from django.db.models import Prefetch, Q
from django.utils import timezone

from asociados.models import Curso
from comercios.models import Comercio
from .models import CategoriaProductoServicio, Novedad, ProductoServicio, Publicidad


ETIQUETAS_CORTAS_CICLO = {
    Curso.DIVISION_CB: "C.B.",
    Curso.DIVISION_CS: "C.S.",
}


def _etiqueta_items(grupo):
    tipos = {item.es_servicio for item in grupo}
    if tipos == {False}:
        return "Producto"
    if tipos == {True}:
        return "Servicio"
    return "Producto o servicio"


def _agrupar_por_precio(items):
    grupos = []
    for tipo_precio, items_iter in groupby(items, key=lambda item: item.tipo_precio):
        items_grupo = list(items_iter)
        grupos.append(
            {
                "tipo_precio": tipo_precio,
                "etiqueta_items": _etiqueta_items(items_grupo),
                "items": items_grupo,
            }
        )
    return grupos


def _anio_ordinal(anio):
    coincidencia = re.fullmatch(r"(\d+)(?:ro|do|to|mo|vo|no)?", anio.lower())
    if not coincidencia:
        return anio
    return f"{coincidencia.group(1)}.º"


def get_categorias_productos_servicios_publicas():
    productos_publicos = ProductoServicio.objects.filter(activo=True).order_by("orden", "nombre")
    return (
        CategoriaProductoServicio.objects.filter(activa=True)
        .prefetch_related(Prefetch("productos_servicios", queryset=productos_publicos, to_attr="items_publicos"))
        .order_by("orden", "nombre")
    )


def get_bloques_productos_publicos(categoria):
    productos = list(
        ProductoServicio.objects.filter(categoria=categoria, activo=True).order_by(
            "ciclo_destinatario",
            "curso_destinatario",
            "orden",
            "nombre",
        )
    )
    etiquetas_ciclo = dict(Curso.DIVISIONES)
    items_generales = [item for item in productos if not item.ciclo_destinatario]
    generales = {"grupos_precio": _agrupar_por_precio(items_generales)} if items_generales else None
    ciclos = []

    items_con_ciclo = (item for item in productos if item.ciclo_destinatario)
    for ciclo, items_ciclo_iter in groupby(items_con_ciclo, key=lambda item: item.ciclo_destinatario):
        etiqueta_corta = ETIQUETAS_CORTAS_CICLO.get(ciclo, ciclo)
        grupos = []
        for curso, items_curso_iter in groupby(items_ciclo_iter, key=lambda item: item.curso_destinatario):
            items_curso = list(items_curso_iter)
            titulo = "Para todo el ciclo" if not curso else f"{_anio_ordinal(curso)} {etiqueta_corta}"
            grupos.append(
                {
                    "titulo": titulo,
                    "grupos_precio": _agrupar_por_precio(items_curso),
                }
            )
        ciclos.append(
            {
                "codigo": ciclo,
                "slug": ciclo.lower(),
                "titulo": etiquetas_ciclo.get(ciclo, ciclo),
                "etiqueta_corta": etiqueta_corta,
                "grupos": grupos,
            }
        )

    return {
        "generales": generales,
        "ciclos": ciclos,
        "mostrar_selector_ciclos": len(ciclos) > 1,
    }


def get_publicidades_home():
    return (
        Publicidad.objects.filter(activa=True)
        .filter(Q(comercio__isnull=True) | Q(comercio__estado=Comercio.ESTADO_FIRMADO))
        .select_related("producto_servicio", "producto_servicio__categoria", "comercio", "comercio__actividad_comercial")
        .order_by("orden", "titulo")
    )


def get_novedades_publicas():
    return Novedad.objects.filter(activa=True, fecha_publicacion__lte=timezone.now()).order_by(
        "-destacada",
        "-fecha_publicacion",
        "titulo",
    )
