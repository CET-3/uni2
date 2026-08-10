---
type: "Pantalla"
title: "Navegación global"
description: "Home única, menú de usuario y barra de navegación."
tags: [mvp, pantalla, navegacion]
timestamp: 2026-06-29T00:00:00-03:00
---

# Navegación global

## Home única

La raíz (`/`) siempre muestra la home y adapta su hero según [USUARIO-018](../reglas/usuarios.md#usuario-018--home-única-por-experiencia). No existen dashboards separados. El logo enlaza a `/` sin parámetros; para una persona multiperfil esto vuelve a mostrar `Elegí cómo querés ingresar`.

## Barra superior

La barra de navegación se muestra en todas las pantallas internas (asociado, gestión, comercio) y contiene:

- **Logo** → home (`/`).
- **Título contextual** opcional según la pantalla.
- **Menú de usuario** (desplegable con el nombre de la persona).

## Menú de usuario

El menú desplegable se organiza en tres secciones visuales:

### Experiencias

- Lista solamente las experiencias disponibles para el usuario.
- Cada acceso vuelve a la home con `?perfil=asociado`, `?perfil=comercio` o `?perfil=gestion`.
- La experiencia operativa aparece como `Administración`.

### Herramientas

- Admin técnico de Django (solo si `is_staff`).
- Especificación (solo si `gestion.ver_especificacion`).
- Design system (solo si `gestion.ver_design_system`).

### Cuenta

- **Cerrar sesión**.

## Sin memoria de la última experiencia

El sistema no recuerda qué experiencia eligió la persona. Cada ingreso por `/` o por el logo vuelve a evaluar las experiencias disponibles.
