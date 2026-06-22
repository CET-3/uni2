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

**Grupos sugeridos:** Administradores, Atención de mutual, Asociados, Comercios.

**Permisos operativos de gestión:** ver dashboard de gestión, consultar asociados, editar asociados, importar asociados, exportar asociados, cobrar cuotas, ver deudores, administrar períodos de cuota e importar cuotas históricas.

**Campos relevantes:** username, email, password, first_name, last_name, is_active, is_staff, last_login, date_joined.

**Admin técnico:** el listado de usuarios muestra una columna de grupos para facilitar la revisión de roles sin abrir cada usuario.
