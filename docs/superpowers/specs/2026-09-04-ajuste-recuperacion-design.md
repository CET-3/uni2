# Ajuste visual y textual de recuperación de contraseña

**Fecha:** 2026-09-04

## Contexto

El login muestra `Olvidé mi contraseña` como un enlace azul subrayado y
alineado a la derecha. Esa presentación queda visualmente aislada del resto del
formulario. Además, la pantalla posterior usa el título `Revisá tu correo`, que
puede interpretarse como confirmación de un envío aunque el DNI y el email no
coincidan.

La primera versión conservaba una respuesta pública idéntica para datos
válidos e inválidos. Se decidió reemplazar esa protección por una respuesta
explícita: la persona debe saber si no existe una cuenta activa con la
combinación de DNI y email ingresada. Esta decisión acepta que terceros puedan
probar combinaciones y confirmar la existencia de cuentas.

## Diseño aprobado

### Acción en el login

`Olvidé mi contraseña` se presentará como una acción secundaria gris oscura,
sin subrayado permanente y acompañada por un ícono de llave. En hover tendrá un
fondo suave y un color de texto más intenso. El foco de teclado seguirá siendo
visible.

No se convertirá en un segundo botón principal ni competirá visualmente con
`Ingresar`.

### Respuesta de la solicitud

Cuando no existe un asociado activo con usuario activo cuyo DNI y email
coincidan, el sistema conserva el formulario y muestra el error general:

> No encontramos una cuenta activa con ese DNI y email. Revisá los datos
> ingresados.

Cuando la cuenta existe, el sistema abre `Solicitud recibida` y pide revisar el
correo. Una cuenta que ya recibió una solicitud dentro del límite de 15
minutos se considera encontrada y llega a la misma pantalla, pero no genera un
nuevo envío.

El servicio de recuperación devuelve si encontró una cuenta habilitada; la
vista usa ese resultado para decidir entre el error del formulario y la
pantalla posterior. Un resultado positivo no significa que el backend SMTP
haya completado la entrega.

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
- Vista y servicio de recuperación, para comunicar si la cuenta fue
  encontrada sin confundirlo con el resultado de entrega SMTP.
- Templates de cambio de contraseña, confirmación de contraseña y datos
  propios que contienen las acciones principales enumeradas.
- Especificación del caso de uso y del patrón visual.
- Pruebas de presentación y de respuesta explícita.

## Verificación

Las pruebas comprobarán que la acción use su clase e ícono, que una combinación
inexistente muestre el error exacto y que una cuenta existente avance a la
confirmación. También verificarán que el límite temporal conserve el resultado
positivo sin crear otra comunicación, los íconos decorativos de las acciones
principales y la regresión de autenticación, recuperación, cambio de contraseña
y datos propios.

## Fuera de alcance

No cambian la validación sintáctica del formulario, el envío SMTP, el límite de
15 minutos ni la vigencia del enlace.
