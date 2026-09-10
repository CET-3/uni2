from urllib.parse import urlencode, urlsplit, urlunsplit

from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView

from .forms_atencion import FiltroAtencionDiariaForm
from .permissions import (
    GESTION_CONSULTAR_ASOCIADOS, GESTION_CONSULTAR_SOLICITUDES_ASOCIACION,
    GESTION_VER_ATENCION_DIARIA, GESTION_VER_COBROS_EQUIPO,
)
from .selectors_atencion import (
    altas_del_periodo, con_aplicaciones, con_fecha_carga, pagos_cargados_con_otra_fecha,
    pagos_del_periodo, pagos_visibles, preparar_lista_pagos, resumir_altas,
    resumir_pagos, resumir_pagos_historicos, solicitudes_pendientes,
)
from .views import GestionPermissionRequiredMixin


@method_decorator(never_cache, name="dispatch")
class AtencionPermissionMixin(GestionPermissionRequiredMixin):
    permission_required = GESTION_VER_ATENCION_DIARIA


def _url_tablero(query):
    return reverse("gestion:atencion_diaria") + (f"?{query}" if query else "")


class FiltrosAtencionMixin:
    def filtros_contexto(self, context):
        form = FiltroAtencionDiariaForm(self.request.GET, user=self.request.user)
        query = self.request.GET.copy()
        query.pop("page", None)
        context.update(form=form, querystring=query.urlencode(), tablero_url=_url_tablero(query.urlencode()))
        if not form.is_valid():
            return None
        periodo = form.cleaned_data["intervalo"]
        context.update(periodo=periodo, equipo=form.cleaned_data["operador"] == "equipo")
        return periodo

    def paginar(self, context, queryset):
        context["page_obj"] = Paginator(queryset, 25).get_page(self.request.GET.get("page"))


class GestionAtencionDiariaView(AtencionPermissionMixin, FiltrosAtencionMixin, TemplateView):
    template_name = "gestion/atencion_diaria.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        periodo = self.filtros_contexto(context)
        if periodo is None:
            return context
        pagos = pagos_del_periodo(self.request.user, periodo, equipo=context["equipo"])
        context["resumen"] = resumir_pagos(pagos)
        context["historicos"] = resumir_pagos_historicos(self.request.user, periodo, equipo=context["equipo"])
        context["titulo_total"] = {
            "hoy": "Cobrado hoy", "ayer": "Cobrado ayer",
            "esta_semana": "Cobrado esta semana", "personalizado": "Cobrado en el período",
        }[context["form"].cleaned_data["periodo"]]
        self.paginar(context, preparar_lista_pagos(pagos))
        context["otra_fecha"] = pagos_cargados_con_otra_fecha(
            self.request.user, periodo, equipo=context["equipo"],
        ).count()
        context["retorno_pago"] = urlencode({"volver": context["tablero_url"]})
        if self.request.user.has_perm(GESTION_CONSULTAR_ASOCIADOS):
            context["altas"] = resumir_altas(periodo)
        if self.request.user.has_perm(GESTION_CONSULTAR_SOLICITUDES_ASOCIACION):
            context["solicitudes"] = solicitudes_pendientes()
        return context


class GestionAtencionCargasView(AtencionPermissionMixin, FiltrosAtencionMixin, TemplateView):
    template_name = "gestion/atencion_cargas.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        periodo = self.filtros_contexto(context)
        if periodo is not None:
            pagos = pagos_cargados_con_otra_fecha(self.request.user, periodo, equipo=context["equipo"])
            self.paginar(context, preparar_lista_pagos(pagos))
            context["mostrar_carga"] = True
            context["retorno_pago"] = urlencode({"volver": context["tablero_url"]})
        return context


class GestionAtencionAltasView(AtencionPermissionMixin, FiltrosAtencionMixin, TemplateView):
    template_name = "gestion/atencion_altas.html"

    def test_func(self):
        return super().test_func() and self.request.user.has_perm(GESTION_CONSULTAR_ASOCIADOS)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        periodo = self.filtros_contexto(context)
        if periodo is not None:
            self.paginar(context, altas_del_periodo(periodo))
        return context


class GestionAtencionPagoView(AtencionPermissionMixin, TemplateView):
    template_name = "gestion/atencion_pago.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # El detalle usa la misma frontera de autorización que los totales.
        pagos = pagos_visibles(self.request.user, equipo=self.request.user.has_perm(GESTION_VER_COBROS_EQUIPO))
        pago = get_object_or_404(preparar_lista_pagos(con_aplicaciones(con_fecha_carga(pagos))), pk=kwargs["pago_id"])
        context["pago"] = pago
        context["aplicaciones"] = pago.aplicaciones.select_related("cuota__periodo__ciclo_lectivo").order_by(
            "cuota__periodo__ciclo_lectivo__anio", "cuota__periodo__mes", "pk",
        )
        context["donaciones"] = pago.donaciones.order_by("pk")
        context["diferencia"] = pago.diferencia_aplicaciones
        try:
            candidate = urlsplit(self.request.GET.get("volver", ""))
        except ValueError:
            candidate = urlsplit("")
        context["tablero_url"] = (
            urlunsplit(("", "", candidate.path, candidate.query, ""))
            if not candidate.scheme and not candidate.netloc and candidate.path == reverse("gestion:atencion_diaria")
            else reverse("gestion:atencion_diaria")
        )
        return context
