from pathlib import Path

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404
from django.views.generic import TemplateView


BASE_ESPECIFICACION = Path(settings.BASE_DIR) / "especificacion"


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        return self.request.user.is_staff


class IndiceView(StaffRequiredMixin, TemplateView):
    template_name = "especificacion/archivo.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ruta_md = BASE_ESPECIFICACION / "index.md"
        context["contenido_md"] = ruta_md.read_text(encoding="utf-8")
        context["titulo"] = "Especificación - Índice"
        context["ruta_relativa"] = "index.md"
        return context


class ArchivoView(StaffRequiredMixin, TemplateView):
    template_name = "especificacion/archivo.html"

    def get(self, request, *args, **kwargs):
        ruta = kwargs.get("ruta", "")
        if not ruta.endswith(".md"):
            ruta = f"{ruta}.md"

        archivo = (BASE_ESPECIFICACION / ruta).resolve()

        # Path traversal protection
        try:
            archivo.relative_to(BASE_ESPECIFICACION.resolve())
        except ValueError:
            raise Http404("Archivo no válido")

        if not archivo.exists() or not archivo.is_file():
            raise Http404("Archivo no encontrado")

        contenido = archivo.read_text(encoding="utf-8")
        context = self.get_context_data(contenido_md=contenido, titulo=f"Especificación - {ruta}", ruta_relativa=ruta)
        return self.render_to_response(context)
