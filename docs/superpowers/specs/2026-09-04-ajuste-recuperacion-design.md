# Ajuste visual y textual de recuperación de contraseña

**Fecha:** 2026-09-04

## Contexto

El login muestra `Olvidé mi contraseña` como un enlace azul subrayado y
alineado a la derecha. Esa presentación queda visualmente aislada del resto del
formulario. Además, la pantalla posterior usa el título `Revisá tu correo`, que
puede interpretarse como confirmación de un envío aunque el DNI y el email no
coincidan.

La recuperación debe conservar una respuesta pública idéntica para datos
válidos e inválidos, porque revelar la coincidencia permitiría consultar qué
cuentas existen.

## Diseño aprobado

### Acción en el login

`Olvidé mi contraseña` se presentará como una acción secundaria gris oscura,
sin subrayado permanente y acompañada por un ícono de llave. En hover tendrá un
fondo suave y un color de texto más intenso. El foco de teclado seguirá siendo
visible.

No se convertirá en un segundo botón principal ni competirá visualmente con
`Ingresar`.

### Respuesta de la solicitud

La pantalla posterior se mantendrá idéntica para cualquier solicitud válida a
nivel de formulario. El título será `Solicitud recibida` y el texto explicará:

> Por seguridad no informamos si los datos coinciden. Si corresponden a una
> cuenta habilitada, vas a recibir un correo con los pasos para elegir una
> contraseña nueva.

El cambio es solamente de presentación. Un DNI o email que no coincide
continúa sin crear una comunicación ni enviar un correo.

### Íconos en acciones principales

Las acciones operativas incorporadas por los recorridos de acceso y
autogestión llevarán un Bootstrap Icon acorde:

- `Guardar contraseña`: `bi-key`.
- `Enviar instrucciones`: `bi-envelope-arrow-up`.
- `Solicitar un enlace nuevo`: `bi-envelope`.
- `Guardar cambios`: `bi-check-lg`.

Los enlaces de navegación `Cancelar`, `Volver` e `Ingresar a UNI2` permanecen
sin ícono. Todos los íconos son decorativos, declaran `aria-hidden="true"` y no
reemplazan el texto visible de la acción.

## Componentes afectados

- Template del login.
- Hoja del design system, con una clase específica y reutilizable para esta
  acción secundaria.
- Template de confirmación de la solicitud.
- Templates de cambio de contraseña, confirmación de contraseña y datos
  propios que contienen las acciones principales enumeradas.
- Especificación del caso de uso y del patrón visual.
- Pruebas de presentación y de respuesta neutra.

## Verificación

Las pruebas comprobarán que la acción use su clase e ícono, que el nuevo texto
no afirme un envío y que las respuestas para datos válidos e inexistentes sigan
siendo indistinguibles. También comprobarán los íconos decorativos de las
acciones principales y ejecutarán la regresión de autenticación, recuperación,
cambio de contraseña y datos propios.

## Fuera de alcance

No cambian la validación del formulario, la búsqueda de la cuenta, el envío de
correo, el límite temporal ni la vigencia del enlace.
