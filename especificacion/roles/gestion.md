---
type: "Rol"
title: "Gestión"
description: "El acceso a gestion no depende de is_staff . is_staff queda reservado para el admin técnico de Django."
tags: [mvp, rol]
timestamp: 2026-06-22T00:00:00-03:00
---

# Gestión

Usuario con uno o más permisos operativos de gestión. Puede acceder solo a las tareas autorizadas:

- Gestionar asociados e importarlos.
- Crear usuarios para asociados mediante las herramientas administrativas habilitadas.
- Gestionar cuotas y registrar pagos.
- Consultar reportes.
- Consultar las herramientas o datos autorizados para sus grupos.

El acceso a `gestion` no depende de `is_staff`. `is_staff` queda reservado para el admin técnico de Django.

Los grupos operativos iniciales y sus alcances se definen en
[Usuarios](../reglas/usuarios.md#usuario-019--matriz-inicial-de-grupos). Los
grupos son acumulables. Tener un permiso de gestión permite entrar únicamente a
las pantallas correspondientes; no habilita por sí solo los modelos del admin.

Las importaciones masivas de padrón y cuotas históricas son tareas de puesta en
marcha reservadas al superusuario `Administrador de la app`, no a la operación
regular de la mutual.
