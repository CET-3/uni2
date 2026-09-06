---
type: "Decisión de arquitectura"
title: "Botones y envíos de formularios"
description: "Patrón compartido de acciones, feedback y protección frente a reintentos."
tags: [arquitectura, frontend, pwa]
timestamp: 2026-09-05T00:00:00-03:00
---

# Botones y envíos de formularios

## Responsabilidades

`static/js/uni2-actions.js`, incluido una vez desde `templates/base.html`,
gestiona todos los formularios POST de las experiencias pública, asociados,
comercios y gestión. Usa un listener delegado de `submit` en captura; también
cubre formularios agregados después y dentro de modales. Volver a cargar el
módulo no registra otro listener. Los GET conservan su comportamiento de navegación.

El estado por formulario bloquea inmediatamente los intentos siguientes, marca
`data-submitting` y `aria-busy`, y deshabilita sus controles de envío, incluidos
los asociados mediante el atributo `form`. No deshabilita los campos de datos.
Una copia oculta conserva el `name/value` del botón pulsado, que de otro modo
se perdería al deshabilitarlo.

El módulo no agrega eventos táctiles ni ejecuta requests por `click`. Las
validaciones nativas se mantienen. Si otro listener cancela el envío (por
ejemplo, la PWA sin conexión), se restaura el estado. `pageshow` restaura los
controles al regresar con Atrás, sin habilitar controles que ya estaban
deshabilitados. No existe un temporizador que habilite un POST mientras sigue
en curso: el documento nuevo muestra los errores o mensajes Django.

## Textos y presentación

```html
<button type="submit" class="btn btn-primary" data-loading-text="Guardando…">
  Guardar
</button>
```

El texto predeterminado es `Procesando…`. El spinner Bootstrap es pequeño,
decorativo y acompañado por texto. Una región `role="status"` anuncia cambios.
Se reserva espacio para los estados sin perder el ancho responsive. Los
colores, foco y estado `:active` siguen siendo los de Bootstrap y Uni2; el CSS
común agrega una transición de 120 ms y respeta `prefers-reduced-motion`.

En los formularios tradicionales el éxito se informa en la página destino con
los mensajes existentes; no se muestra «Guardado» antes de conocer el resultado.

## Acciones asíncronas

```javascript
try {
  await window.Uni2Actions.run(button, async () => {
    const response = await fetch(url, options);
    if (!response.ok) throw new Error('La operación no se pudo completar');
    return response.json();
  });
} catch (error) {
  // Mostrar el error mediante el mecanismo habitual de esta pantalla.
}
```

`run` invoca la función una sola vez mientras el botón esté ocupado. El
consumidor debe incluir toda la operación dentro de esa función, validar la
respuesta y mostrar sus errores. Al resolver, muestra un check y
`data-success-text` (predeterminado `Guardado`) durante 1200 ms; al rechazar,
restaura el botón y propaga el error. `Uni2Actions.reset(elemento)` permite
restauración explícita. Los callbacks viejos no deben sobrescribir un estado
restaurado o una acción posterior.

La limpieza local previa al logout usa `uni2:before-submit` y
`event.detail.waitUntil(promesa)`. El módulo espera y reanuda con `requestSubmit`
una sola vez; el logout sigue funcionando si IndexedDB falla o supera 1200 ms.
No usa `form.submit()`. La limpieza de credencial no es una confirmación de
cierre de sesión: el POST sigue siendo necesario.

## Cobertura y revisión de patrones

Se migraron preinscripción y correcciones, login y contraseñas, logout desktop
y móvil, altas y edición de asociados, datos propios, cobros/donaciones,
creación y generación de períodos, análisis y confirmación de importaciones,
revisión de solicitudes y reenvío de sus correos, validación de credenciales,
y guardado/eliminación local de credenciales (incluido el modal de consentimiento).

La investigación no encontró handlers inline de envío, mezcla click/touch ni
fetch de escritura en preinscripción. Su submit nativo no bloqueaba un segundo
intento. Se reprodujo que dos POST devolvían primero confirmación y después
el error de documento existente. Esto explica el resultado reportado, aunque
no prueba por qué el teléfono originó dos eventos a partir de un toque percibido.
El logout tenía una espera asíncrona sin bloqueo del formulario y terminaba con
`HTMLFormElement.prototype.submit.call(form)`; también se reemplazó ese patrón.
Los eventos touch del carrusel sólo pausan el movimiento. El service worker
realiza un único fetch de las mutaciones y no encola ni reintenta POST.

Los filtros GET y el modal de comercio (fetch de lectura) no necesitan bloqueo
de escritura. El admin técnico usa otra base y queda pendiente de una adaptación
específica a sus controles; pagos, cuotas, donaciones y solicitudes son de sólo
lectura allí. Cualquier nuevo fetch de escritura debe adoptar `run` y una
protección de negocio en backend. Pedidos, tickets y contabilidad avanzada
siguen fuera de alcance.

## Protección en servidor

Las [preinscripciones](../reglas/solicitudes-asociacion.md) y los
[cobros](../reglas/pagos.md) llevan una clave de operación persistida y única.
Las claves no sustituyen permisos, CSRF ni validaciones. Deben conservarse al
reintentar el mismo formulario; abrir uno nuevo genera una nueva clave.

Se conservan las defensas existentes: cuota única por asociado/período,
generación con transacción y `get_or_create`, asociado con DNI único,
solicitud no cancelada con documento normalizado único, transiciones de
solicitud con bloqueo de fila y comunicaciones con clave única.

Los dos campos nuevos permiten NULL para registros históricos. Las migraciones
no reinterpretan ni modifican pagos o solicitudes existentes. Las llamadas
internas antiguas sin clave conservan compatibilidad; los formularios públicos
de preinscripción y de cobro sí la exigen. Una página abierta antes del deploy
debe recargarse y muestra un mensaje explícito si falta la clave.

## Pruebas

`tests/frontend/test_actions_browser.py` usa pytest, un servidor HTTP local y
Chromium real, sin framework JS. Comprueba requests reales, bloqueo inmediato,
submitter, validación, cancelación, restauración, espera asíncrona, formulario
real de preinscripción, offline y ancho responsive con Bootstrap. La variante
angosta renderiza el formulario a 390 px; los eventos se generan por código,
por lo que no reemplaza la comprobación en un teléfono físico.

Ejecutar `DB_ENGINE=sqlite .venv/bin/pytest tests/frontend -q`. Sin Chromium,
estas pruebas se omiten explícitamente. La suite de servicios y vistas verifica
unicidad, reintentos y efectos secundarios. SQLite no verifica bloqueos de fila;
las pruebas de concurrencia requieren PostgreSQL compatible con Django.
El job PostgreSQL de GitHub Actions ejecuta `cuotas/tests/test_idempotencia.py`,
incluido el caso concurrente que SQLite omite.
