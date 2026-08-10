# Plan: URL compartida para la credencial

**Estado:** implementado el 10 de agosto de 2026.

Este documento registra la evolución aplicada al QR de Mi credencial. El QR
contiene la URL neutral y el formulario manual continúa disponible como
respaldo.

## Objetivo

Reemplazar el contenido del QR por una URL de Uni2 que pueda abrirse con la
cámara común de un teléfono. La misma URL debe llevar al asociado a su propia
credencial y permitir que un comercio habilitado la valide, siempre aplicando
los permisos en el servidor.

La URL identifica una credencial, pero no concede acceso. Conocerla, recibirla
o encontrarla en el historial no debe alcanzar para ver datos personales ni
para validar una credencial.

## URL propuesta

Usar una ruta neutral, sin nombrar al rol que la abre:

```text
/credenciales/<uuid:token>/
```

Ejemplo completo:

```text
https://uni2.example.com/credenciales/550e8400-e29b-41d4-a716-446655440000/
```

El QR debe codificar la URL absoluta del entorno actual. No debe incluir
nombre, DNI, número de asociado, estado, deuda ni cuotas.

## Comportamiento según el usuario

| Situación | Respuesta esperada |
|---|---|
| Asociado autenticado y dueño del token | Muestra su pantalla Mi credencial. |
| Asociado autenticado y token ajeno | Rechaza el acceso sin confirmar si el token existe. |
| Comercio autenticado con convenio firmado | Valida contra el estado actual y muestra sólo el resultado permitido. |
| Comercio sin convenio firmado | Rechaza la validación con un mensaje claro. |
| Usuario autenticado sin un rol admitido | Rechaza el acceso. |
| Persona sin sesión | Solicita iniciar sesión y luego vuelve a la misma URL. |
| Token inexistente o con formato inválido | Muestra una respuesta genérica, sin datos de asociados. |

No se debe redirigir a un asociado hacia la credencial encontrada antes de
comprobar que `request.user.asociado.token_credencial` coincide con el token de
la URL.

## Experiencia esperada

### Para el asociado

1. Inicia sesión y abre Mi credencial.
2. La pantalla muestra sus datos permitidos y un QR con la URL compartida.
3. Puede presentar el QR en un comercio.
4. Si abre esa URL con su propia sesión, vuelve a ver únicamente su
   credencial.
5. La copia offline puede mostrar el mismo QR, pero debe mantener el aviso de
   que sólo el servidor conectado confirma la vigencia.

### Para el comercio

1. Escanea el QR con la cámara común del teléfono.
2. El navegador abre la URL en Uni2.
3. Si todavía no inició sesión, se autentica y regresa a la URL escaneada.
4. Uni2 comprueba que el usuario esté vinculado a un comercio con convenio
   firmado.
5. El servidor consulta el token y el estado actual del asociado.
6. Muestra válida o inválida y, cuando corresponde, nombre y apellido, tipo y
   estado. No muestra deuda ni otros datos sensibles.

El formulario manual de validación se conserva como alternativa cuando la
cámara no pueda leer el QR y acepta el UUID o el DNI. El DNI se envía por POST:
no forma parte de la URL ni del QR.

## Autorización y privacidad

- Todas las decisiones de acceso se realizan en Django; JavaScript y el QR no
  son controles de permisos.
- El token continúa siendo un UUID aleatorio y único. No se reemplaza por el
  ID ni por el número correlativo del asociado.
- La vista del asociado exige que la cuenta autenticada sea la propietaria
  exacta del token.
- La validación exige un comercio autenticado y con convenio firmado.
- Un rechazo por token ajeno o inexistente no debe revelar nombre, estado ni
  la existencia de una cuenta.
- La respuesta debe usar `Cache-Control: private, no-store` y no debe entrar
  en Cache Storage.
- La página debe evitar enviar la URL como referente a otros orígenes mediante
  una política `Referrer-Policy` adecuada.
- Los eventos de auditoría y mensajes de error no deben copiar el token en sus
  campos descriptivos.
- Antes de implementar se debe revisar el registro de requests de Producción,
  porque una URL con token puede quedar en logs, historial y capturas. Cuando
  sea posible, el token se debe redactar en los logs de acceso.

El token no se considera una contraseña, pero su exposición facilita intentos
de consulta y por eso debe tratarse como dato privado. Los permisos siguen
siendo obligatorios incluso si el UUID es válido.

## Separación de responsabilidades

- `urls.py`: declara la ruta neutral.
- `views.py`: autentica, reconoce el rol y compone la respuesta HTTP.
- `selectors.py`: busca la credencial por token sin incluir reglas de acceso.
- `services.py`: decide el resultado de validación para un comercio y conserva
  las reglas de negocio existentes.
- templates: presentan la credencial propia o el resultado limitado; no
  consultan modelos ni deciden permisos.
- JavaScript de credencial: genera el QR a partir de la URL entregada por el
  servidor y mantiene la copia offline consentida.

La resolución neutral puede vivir en la app `usuarios`, porque reconoce el rol
autenticado, mientras que la pantalla propia permanece en `asociados` y la
validación permanece en `comercios`. La vista neutral debe redirigir o delegar
sin duplicar las reglas de esos dominios.

## Plan de implementación

### Etapa 1: contrato y permisos

1. Agregar tests que expresen la matriz de permisos de este documento.
2. Declarar la ruta neutral con conversor UUID.
3. Implementar la resolución por rol y conservar el parámetro `next` durante
   el login.
4. Reutilizar la validación existente de `comercios.services`.
5. Comprobar en el servidor la propiedad de la credencial para asociados.

### Etapa 2: QR y pantallas

1. Construir la URL absoluta en la vista de Mi credencial.
2. Cambiar el QR online para codificar esa URL.
3. Guardar también la URL necesaria en la copia offline o reconstruirla de
   forma segura desde el origen y el token.
4. Mantener visible el UUID escrito y el formulario manual como respaldo.
5. Ajustar los textos para explicar que escanear abre Uni2 y que la vigencia
   se confirma con conexión.

### Etapa 3: endurecimiento

1. Verificar encabezados `private, no-store` y `Referrer-Policy`.
2. Revisar y, si hace falta, redactar el token en logs de acceso y auditoría.
3. Probar que el service worker nunca almacene la respuesta autenticada.
4. Probar expiración, cambio de usuario y eliminación de la copia offline.
5. Ejecutar pruebas manuales en Android e iOS con cámara común, navegador y
   PWA instalada.

### Etapa 4: documentación vigente

Cuando se implemente, actualizar en el mismo cambio:

- las reglas de credenciales;
- el caso de uso de validación;
- las pantallas de asociado, comercio y PWA;
- las pruebas manuales;
- este documento, cambiando su estado y retirando las diferencias con el
  comportamiento vigente.

## Pruebas mínimas

- El QR contiene una URL del mismo origen y no sólo el UUID.
- Un asociado puede abrir la URL de su propio token.
- Un asociado no puede abrir la URL de otro asociado.
- Un comercio firmado puede validar un token activo e inactivo.
- Un comercio no firmado no puede validar.
- Una persona anónima vuelve a la URL original después del login.
- Un rol no admitido recibe acceso denegado.
- Un UUID inexistente no revela información.
- La respuesta no se almacena en caché.
- El QR guardado offline abre la misma ruta, pero no afirma vigencia sin red.
- El ingreso manual del token continúa funcionando.

## Fuera de este plan

- Hacer pública la credencial por conocer la URL.
- Incorporar DNI, deuda o cuotas al QR o al resultado del comercio.
- Reemplazar la autenticación por posesión del token.
- Implementar tokens rotativos o de un solo uso.
- Eliminar la alternativa de validación manual.

Los tokens temporales pueden evaluarse más adelante si el análisis de riesgo
lo justifica, pero no son necesarios para que el QR sea útil en el MVP.
