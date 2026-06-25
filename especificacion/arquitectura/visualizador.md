---
type: "Arquitectura"
title: "Visualizador de especificación"
description: "App interna para que desarrolladores staff lean la especificación desde el navegador."
tags: [arquitectura, visualizador]
timestamp: 2026-06-24T23:00:00-03:00
---

# Visualizador de especificación

## Propósito

Los alumnos que desarrollan sobre la app necesitan poder leer la especificación (archivos Markdown en `especificacion/`) desde el navegador, sin tener que abrir los archivos en el editor.

## App

`especificacion` — app separada por dominio, no mezclada con `gestion` ni `web`.

## Acceso

Solo usuarios con `is_staff=True`. Usa `LoginRequiredMixin` + `UserPassesTestMixin` (patrón `StaffRequiredMixin`).

## Cómo funciona

- `IndiceView` lee `especificacion/index.md`, lo renderiza a HTML con `python-markdown` y lo muestra.
- `ArchivoView` recibe una ruta por URL, valida que no haya path traversal con `Path.relative_to()`, lee el archivo `.md`, lo renderiza a HTML y lo muestra.
- Ambos usan el template `especificacion/archivo.html` que extiende `base.html`.

## URL

```
especificacion/        → IndiceView   (name: indice)
especificacion/<path>  → ArchivoView  (name: archivo)
```

## Renderizado

Usa `python-markdown` con extensión `fenced_code`. El HTML se inyecta con `{{ contenido_html|safe }}` en el template. No se renderiza a texto plano.

## Link en navegación

Aparece como "Especificación" en el menú desplegable del usuario, solo cuando `user.is_staff == True`.
