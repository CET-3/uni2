# Entrega: botones y protección de envíos

Cambios preparados para PR hacia `staging` y publicación mediante el workflow
`Deploy staging`, con aplicación previa de las migraciones compatibles.

## Diagnóstico

Se reprodujo el resultado de preinscripción reportado: un primer POST válido
redirige a recepción; repetirlo mostraba el conflicto de documento existente.
El formulario no tenía bloqueo durante el envío. No se encontraron handlers
de envío duplicados, onclick, mezcla click/touch ni fetch de escritura en esa
pantalla. No se comprobó en un teléfono físico el origen del segundo evento.

El logout PWA tenía otro recorrido vulnerable: un handler asíncrono permitía
iniciar varias limpiezas y luego hacía submit manual. Se reemplazó por una
espera coordinada con el módulo común.

## Mecanismo y cobertura

El [módulo común](../../static/js/uni2-actions.js) bloquea los POST desde submit,
deshabilita los botones, conserva sus valores, muestra texto y spinner,
respeta accesibilidad y recupera el estado ante cancelación o al volver con
Atrás. `Uni2Actions.run` gestiona acciones asíncronas, éxito y restauración
ante errores. No agrega dependencias.

Se configuraron textos en preinscripción/correcciones, login/contraseñas,
logout, altas/edición/datos propios, cobros y donaciones, períodos e
importaciones, gestión de solicitudes y validación de credenciales. También
se migraron las acciones locales de credencial y su modal de consentimiento.

El admin técnico usa otra base y queda pendiente de una adaptación propia.
Los filtros GET y el modal de comercio sólo consultan datos y no necesitan
bloqueo de escritura. Las nuevas acciones AJAX de escritura deben utilizar
el helper y una protección de negocio en servidor.

## Backend

- Preinscripción: UUID único por envío. El reintento de la misma operación
  vuelve a confirmar recepción sin duplicar solicitud, auditoría, token ni
  correo. Otro formulario con el mismo documento conserva el error habitual.
- Cobros/donaciones: UUID único por operación y bloqueo transaccional del
  asociado antes de consultar deuda. Repetir una operación no crea otro ingreso.
- Se conservan las protecciones existentes de cuotas por asociado/período,
  DNI de asociado, documento de solicitud, transiciones y comunicaciones.
- Dos migraciones agregan campos UUID opcionales para los registros históricos;
  los formularios nuevos exigen la clave. Las páginas abiertas antes de esta
  versión deben recargarse si muestran el mensaje de clave ausente.

Las decisiones funcionales y técnicas están en la
[especificación OKF](../../especificacion/arquitectura/acciones-formularios.md).

## Verificación

- Suite completa sin navegador: `DB_ENGINE=sqlite .venv/bin/pytest -q --ignore=tests/frontend`:
  **713 aprobadas, 1 omitida**. La omitida requiere PostgreSQL y prueba dos
  cobros concurrentes; SQLite no implementa `select_for_update`.
- Chromium: `DB_ENGINE=sqlite .venv/bin/pytest tests/frontend/test_actions_browser.py -q`.
  **2 aprobadas**: desktop y formulario a 390 px con reducir movimiento.
  Verifica requests HTTP reales, formulario renderizado de preinscripción,
  bloqueo, recuperación ante error, offline, espera previa al logout,
  restauración, valores del botón y ancho responsive con Bootstrap.
- `manage.py check`, `makemigrations --check --dry-run`, comprobación de
  sintaxis de los tres módulos JS y `git diff --check`: sin errores.
- Dos avisos de deprecación de `CheckConstraint.check` ya existentes en
  `contenidos`; no son fallos de esta implementación.

No se ejecutó la prueba en teléfono físico ni concurrencia real en PostgreSQL.
Las dos migraciones se verificaron en las bases de pruebas, sin aplicarlas a
un ambiente remoto.

## Archivos modificados o agregados

- [.github/workflows/tests.yml](../../.github/workflows/tests.yml)

- [asociados/migrations/0011_solicitudasociacion_clave_operacion.py](../../asociados/migrations/0011_solicitudasociacion_clave_operacion.py)
- [asociados/models.py](../../asociados/models.py)
- [asociados/services.py](../../asociados/services.py)
- [cuotas/migrations/0006_pago_clave_operacion.py](../../cuotas/migrations/0006_pago_clave_operacion.py)
- [cuotas/models.py](../../cuotas/models.py)
- [cuotas/services.py](../../cuotas/services.py)
- [cuotas/tests/test_idempotencia.py](../../cuotas/tests/test_idempotencia.py)
- [docs/informes/2026-09-06-botones-acciones.md](../../docs/informes/2026-09-06-botones-acciones.md)
- [especificacion/arquitectura/acciones-formularios.md](../../especificacion/arquitectura/acciones-formularios.md)
- [especificacion/arquitectura/design-system.md](../../especificacion/arquitectura/design-system.md)
- [especificacion/arquitectura/index.md](../../especificacion/arquitectura/index.md)
- [especificacion/entidades/pago.md](../../especificacion/entidades/pago.md)
- [especificacion/entidades/solicitud-asociacion.md](../../especificacion/entidades/solicitud-asociacion.md)
- [especificacion/reglas/pagos.md](../../especificacion/reglas/pagos.md)
- [especificacion/reglas/solicitudes-asociacion.md](../../especificacion/reglas/solicitudes-asociacion.md)
- [gestion/forms.py](../../gestion/forms.py)
- [gestion/tests/test_views.py](../../gestion/tests/test_views.py)
- [gestion/views.py](../../gestion/views.py)
- [pwa/templates/pwa/offline_credential.html](../../pwa/templates/pwa/offline_credential.html)
- [pwa/tests/test_template_contract.py](../../pwa/tests/test_template_contract.py)
- [pwa/views.py](../../pwa/views.py)
- [static/css/uni2-design-system.css](../../static/css/uni2-design-system.css)
- [static/js/uni2-actions.js](../../static/js/uni2-actions.js)
- [static/pwa/uni2-credential.js](../../static/pwa/uni2-credential.js)
- [static/pwa/uni2-pwa.js](../../static/pwa/uni2-pwa.js)
- [templates/asociados/credencial.html](../../templates/asociados/credencial.html)
- [templates/asociados/datos_propios.html](../../templates/asociados/datos_propios.html)
- [templates/base.html](../../templates/base.html)
- [templates/comercios/validar_credencial.html](../../templates/comercios/validar_credencial.html)
- [templates/gestion/asociado_editar.html](../../templates/gestion/asociado_editar.html)
- [templates/gestion/asociado_form.html](../../templates/gestion/asociado_form.html)
- [templates/gestion/cobrar_cuotas.html](../../templates/gestion/cobrar_cuotas.html)
- [templates/gestion/importar_asociados.html](../../templates/gestion/importar_asociados.html)
- [templates/gestion/importar_cuotas_historicas.html](../../templates/gestion/importar_cuotas_historicas.html)
- [templates/gestion/periodos_cuota.html](../../templates/gestion/periodos_cuota.html)
- [templates/gestion/solicitud_asociacion_accion.html](../../templates/gestion/solicitud_asociacion_accion.html)
- [templates/gestion/solicitud_asociacion_detalle.html](../../templates/gestion/solicitud_asociacion_detalle.html)
- [templates/includes/navbar.html](../../templates/includes/navbar.html)
- [templates/registration/login.html](../../templates/registration/login.html)
- [templates/registration/password_change_form.html](../../templates/registration/password_change_form.html)
- [templates/registration/password_reset_confirm.html](../../templates/registration/password_reset_confirm.html)
- [templates/registration/password_reset_form.html](../../templates/registration/password_reset_form.html)
- [templates/web/preinscripcion.html](../../templates/web/preinscripcion.html)
- [templates/web/solicitud_seguimiento.html](../../templates/web/solicitud_seguimiento.html)
- [tests/frontend/actions.html](../../tests/frontend/actions.html)
- [tests/frontend/test_actions_browser.py](../../tests/frontend/test_actions_browser.py)
- [web/forms.py](../../web/forms.py)
- [web/tests/test_preinscripcion.py](../../web/tests/test_preinscripcion.py)
- [web/views.py](../../web/views.py)
