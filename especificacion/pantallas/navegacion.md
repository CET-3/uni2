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
- **Productos y servicios** → `/#productos-servicios`.
- **Comercios** → `/#beneficios`.
- **Título contextual** opcional según la pantalla.
- **Menú de usuario** (desplegable con el nombre de la persona).

Los dos enlaces públicos llevan a secciones de la home única y no a los listados independientes, cuyas rutas se conservan por compatibilidad. En mobile, al elegir una sección se cierra primero el menú colapsado y luego se realiza la navegación o el desplazamiento. Las secciones contemplan mediante `scroll-margin-top` la navbar sticky, el banner de staging y los safe areas de una PWA instalada.

## Menú de usuario

El menú desplegable se organiza en tres secciones visuales:

### Experiencias

- Lista solamente las experiencias disponibles para el usuario.
- Cada acceso vuelve a la home con `?perfil=asociado`, `?perfil=comercio` o `?perfil=gestion`.
- La experiencia operativa aparece como `Administración`.

### Herramientas

- Admin técnico de Django (solo con `usuarios.acceder_admin_tecnico`; la bandera
  técnica `is_staff` por sí sola no muestra el enlace).
- Especificación (solo si `gestion.ver_especificacion`).
- Design system (solo si `gestion.ver_design_system`).

### Cuenta

- **Mis datos** (solamente cuando existe un asociado vinculado).
- **Cambiar contraseña** (para una cuenta de asociado).
- **Cerrar sesión**.

## Sin memoria de la última experiencia

El sistema no recuerda qué experiencia eligió la persona. Cada ingreso por `/` o por el logo vuelve a evaluar las experiencias disponibles.
