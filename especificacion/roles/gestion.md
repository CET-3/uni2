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
- Crear usuarios para asociados desde el detalle del asociado.
- Gestionar cuotas y registrar pagos.
- Consultar reportes.
- Ver la especificación del proyecto.

El acceso a `gestion` no depende de `is_staff`. `is_staff` queda reservado para el admin técnico de Django.
