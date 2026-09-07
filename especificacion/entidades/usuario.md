---
type: "Entidad"
title: "Usuario"
description: "Usuario de autenticación de Django. Se recomienda usar el sistema estandar inicialmente."
resource: "django.contrib.auth.models.User"
tags: [mvp, modelo-de-datos]
timestamp: 2026-06-22T00:00:00-03:00
---

# Usuario

Usuario de autenticación de Django. Se recomienda usar el sistema estandar inicialmente.

**Grupos iniciales:** Atención al asociado, Administrador de permisos, Gestión
de convenios, Gestión de productos y servicios, Gestión de publicidades,
Administrador de la mutual, Equipo del proyecto y Administrador de la app. Los
grupos son acumulables.

**Grupos de experiencia:** Asociados y Comercios. Estos grupos acompañan al
vínculo con la entidad correspondiente y no reemplazan los grupos operativos.

**Permisos operativos de gestión:** consultar asociados, editar asociados,
importar asociados, exportar asociados, cobrar cuotas, ver deudores,
administrar períodos de cuota, importar cuotas históricas, consultar auditoría y
acceder a la documentación interna. La experiencia administrativa se deduce de
estas capacidades o del acceso al admin técnico.

**Campos relevantes:** username, email, password, first_name, last_name, is_active, is_staff, last_login, date_joined.

**Admin técnico:** el listado de usuarios muestra una columna de grupos para
facilitar la revisión de roles sin abrir cada usuario. Una cuenta activa puede
entrar si tiene algún permiso efectivo sobre un modelo registrado, o si es
superusuario. `is_staff` queda como dato técnico de compatibilidad y no define
por sí solo el acceso.
