---
type: "Pantalla"
title: "Navegación global"
description: "Inicio inteligente, menú de usuario y barra de navegación."
tags: [mvp, pantalla, navegacion]
timestamp: 2026-06-29T00:00:00-03:00
---

# Navegación global

## Inicio inteligente

La raíz del sitio (`/`) redirige según el perfil del usuario, según se define en [USUARIO-018](../reglas/usuarios.md#usuario-018--inicio-inteligente):

| Situación | Destino |
|---|---|
| Visitante sin sesión | Home pública |
| Solo asociado | Home asociado |
| Solo gestión | Home gestión |
| Solo comercio | Home comercio |
| 2+ experiencias | Elegir panel |
| Sin experiencias | Home pública |

El logo (arriba a la izquierda) enlaza a `/` y respeta el mismo criterio.

## Barra superior

La barra de navegación se muestra en todas las pantallas internas (asociado, gestión, comercio) y contiene:

- **Logo** → inicio inteligente (`/`).
- **Título contextual** opcional según la pantalla.
- **Menú de usuario** (desplegable con el nombre de la persona).

## Menú de usuario

El menú desplegable se organiza en tres secciones visuales:

### Paneles

- Si el usuario tiene una sola experiencia: acceso directo a ese panel.
- Si tiene más de una: lista de paneles disponibles.
- Gestión aparece como "Panel de gestión".

### Herramientas

- Admin técnico de Django (solo si `is_staff`).
- Especificación (solo si `gestion.ver_especificacion`).
- Design system (solo si `gestion.ver_design_system`).

### Cuenta

- **Sitio público** — siempre visible, lleva a la home pública.
- **Cerrar sesión**.

## Sin memoria de último panel

En el MVP el sistema no recuerda qué panel usó la persona en su visita anterior. Cada vez que se ingresa por `/` o por el logo, se vuelven a evaluar las experiencias disponibles.
