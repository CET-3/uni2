import os
import re
from pathlib import Path

import markdown as md

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404
from django.views.generic import TemplateView


BASE_ESPECIFICACION = Path(settings.BASE_DIR) / "especificacion"


def _rewrite_md_links(html: str, ruta_relativa: str) -> str:
    """Rewrite relative .md links to absolute URLs."""
    base_dir = str(Path(ruta_relativa).parent)
    if base_dir == ".":
        base_dir = ""

    def _replace(m):
        href = m.group(1)
        if not href.endswith(".md") or href.startswith(("http://", "https://", "#", "/")):
            return m.group(0)
        resolved = os.path.normpath(f"{base_dir}/{href}" if base_dir else href)
        return m.group(0).replace(f'href="{href}"', f'href="/especificacion/{resolved}/"')

    return re.sub(r'href="([^"]+)"', _replace, html)


def _render_markdown(texto: str, ruta_relativa: str = "") -> str:
    html = md.markdown(texto, extensions=["fenced_code"])
    if ruta_relativa:
        html = _rewrite_md_links(html, ruta_relativa)
    return html


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        return self.request.user.is_staff


class IndiceView(StaffRequiredMixin, TemplateView):
    template_name = "especificacion/archivo.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ruta_md = BASE_ESPECIFICACION / "index.md"
        context["contenido_html"] = _render_markdown(ruta_md.read_text(encoding="utf-8"), ruta_relativa="index.md")
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

        contenido = _render_markdown(archivo.read_text(encoding="utf-8"), ruta_relativa=ruta)
        context = self.get_context_data(contenido_html=contenido, titulo=f"Especificación - {ruta}", ruta_relativa=ruta)
        return self.render_to_response(context)
