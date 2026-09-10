from urllib.parse import urlencode
from datetime import timedelta

from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Count, Subquery
from django.http import Http404
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView

from .forms_metricas import FiltroMetricasForm
from .permissions import GESTION_VER_METRICAS
from .selectors_metricas import personas_metricas, cuotas_vencidas_metricas, solicitudes_del_periodo
from .services_metricas import construir_metricas
from .views import GestionPermissionRequiredMixin


@method_decorator(never_cache, name="dispatch")
class MetricasBaseView(GestionPermissionRequiredMixin, TemplateView):
    permission_required = GESTION_VER_METRICAS

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = FiltroMetricasForm(self.request.GET)
        query = self.request.GET.copy()
        query.pop("page", None)
        context["querystring"] = query.urlencode()
        return context


class GestionMetricasView(MetricasBaseView):
    template_name = "gestion/metricas.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not context["form"].is_valid():
            return context
        filtros = context["form"].cleaned_data
        context.update(periodo=filtros["intervalo"], comparacion=filtros["comparacion"])
        datos = construir_metricas(filtros["intervalo"], filtros["comparacion"], filtros["tipo"])

        def enlace(categoria, **extra):
            params = {"periodo": filtros["periodo"], "tipo": filtros["tipo"], "comparar": filtros["comparar"],
                "desde": filtros["intervalo"].desde, "hasta": filtros["intervalo"].hasta, "categoria": categoria, **extra}
            return reverse("gestion:metricas_detalle") + "?" + urlencode(params)

        puede_personas = self.request.user.has_perm("gestion.consultar_asociados")
        for fila in datos["padron"]["serie"]:
            for categoria in ("altas", "bajas"):
                fila[f"url_{categoria}"] = enlace(categoria, periodo="personalizado", desde=fila["desde"], hasta=fila["hasta"]) if puede_personas else None
        context["altas_url"] = enlace("altas") if puede_personas else None
        context["bajas_url"] = enlace("bajas") if puede_personas else None
        for fila in datos["deuda"]["grupos"]:
            fila["url"] = enlace("deuda", grupo=fila["grupo"]) if puede_personas and self.request.user.has_perm("gestion.ver_deudores") else None
        for fila, edad in zip(datos["deuda"]["antiguedad"], ("30", "60", "mas60")):
            fila["url"] = enlace("deuda", edad=edad) if puede_personas and self.request.user.has_perm("gestion.ver_deudores") else None
        for fila in datos["solicitudes"]["estados"]:
            fila["url"] = enlace("solicitudes", estado=fila["estado"]) if self.request.user.has_perm("gestion.consultar_solicitudes_asociacion") else None
        for fila in datos["composicion"]["clasificaciones"]:
            fila["url"] = enlace("clasificacion", clasificacion=fila["id"] or "sin") if puede_personas else None
        context.update(datos=datos, graficos={"padron": datos["padron"]["serie"], "cuotas": datos["cuotas"]["serie"]})
        return context


class GestionMetricasDetalleView(MetricasBaseView):
    template_name = "gestion/metricas_detalle.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categoria = self.request.GET.get("categoria")
        if categoria not in ("altas", "bajas", "deuda", "solicitudes", "clasificacion"):
            raise Http404
        permiso = "gestion.consultar_solicitudes_asociacion" if categoria == "solicitudes" else "gestion.consultar_asociados"
        if not self.request.user.has_perm(permiso) or (categoria == "deuda" and not self.request.user.has_perm("gestion.ver_deudores")):
            raise PermissionDenied
        context["categoria"] = categoria
        if not context["form"].is_valid():
            return context
        filtros = context["form"].cleaned_data
        periodo = filtros["intervalo"]
        context["periodo"] = periodo
        personas = personas_metricas(filtros["tipo"])
        if categoria in ("altas", "bajas"):
            campo = "fecha_alta" if categoria == "altas" else "fecha_baja"
            objetos = personas.filter(**{f"{campo}__range": (periodo.desde, periodo.hasta)})
            titulo = "Altas del período" if categoria == "altas" else "Bajas del período"
        elif categoria == "deuda":
            edad = self.request.GET.get("edad")
            deudas = cuotas_vencidas_metricas(filtros["tipo"])
            grupo = self.request.GET.get("grupo", "3")
            if edad not in (None, "30", "60", "mas60") or grupo not in ("1", "2", "3"):
                raise Http404
            if edad:
                hoy = timezone.localdate()
                if edad == "30":
                    deudas = deudas.filter(periodo__fecha_vencimiento__gte=hoy - timedelta(days=30))
                elif edad == "60":
                    deudas = deudas.filter(periodo__fecha_vencimiento__lt=hoy - timedelta(days=30), periodo__fecha_vencimiento__gte=hoy - timedelta(days=60))
                else:
                    deudas = deudas.filter(periodo__fecha_vencimiento__lt=hoy - timedelta(days=60))
                objetos = personas.filter(pk__in=Subquery(deudas.values("asociado_id")))
                titulo = "Personas con deuda vencida · " + {"30": "hasta 30 días", "60": "31 a 60 días", "mas60": "más de 60 días"}[edad]
            else:
                por_persona = deudas.order_by().values("asociado_id").annotate(numero=Count("pk"))
                por_persona = por_persona.filter(numero__gte=3) if grupo == "3" else por_persona.filter(numero=int(grupo))
                objetos = personas.filter(pk__in=Subquery(por_persona.values("asociado_id")))
                titulo = f"Personas con {grupo}{'+' if grupo == '3' else ''} cuotas vencidas · hoy"
        elif categoria == "solicitudes":
            from asociados.models import SolicitudAsociacion
            estado = self.request.GET.get("estado")
            if estado not in dict(SolicitudAsociacion.ESTADOS):
                raise Http404
            objetos = solicitudes_del_periodo(periodo, filtros["tipo"]).filter(estado=estado)
            titulo = "Solicitudes del período · " + dict(SolicitudAsociacion.ESTADOS)[estado]
        else:
            clasificacion = self.request.GET.get("clasificacion", "sin")
            if clasificacion != "sin" and not clasificacion.isdecimal():
                raise Http404
            objetos = personas_metricas("adherente").filter(estado="activo", clasificacion_adherente_id=None if clasificacion == "sin" else int(clasificacion))
            titulo = "Adherentes activos por clasificación · hoy"
        context.update(titulo=titulo, page_obj=Paginator(objetos.order_by("apellido", "nombre", "pk"), 25).get_page(self.request.GET.get("page")))
        query = self.request.GET.copy()
        for campo in ("categoria", "estado", "grupo", "edad", "clasificacion", "page"):
            query.pop(campo, None)
        context["tablero_url"] = reverse("gestion:metricas") + "?" + query.urlencode()
        return context
