# Refresco de staging con usuarios fieles

## Objetivo

Permitir que staging se refresque desde Producción conservando exactamente las
cuentas de usuario copiadas: contraseñas, estado, grupos, permisos,
`is_staff`, `is_superuser` y relaciones con asociados o comercios. El cambio no
debe eliminar ni crear usuarios para reemplazar a los usuarios productivos.

La base continúa siendo una copia de datos productivos y debe tratarse con el
mismo nivel de sensibilidad que Producción.

## Decisión aprobada

Se adopta el modo **copia fiel de usuarios**.

El endurecimiento posterior a la restauración hará únicamente lo siguiente:

- eliminar todas las sesiones Django copiadas;
- conservar sin modificaciones las filas de `auth_user` y sus relaciones,
  incluidas contraseñas, estado, grupos, permisos, privilegios y perfiles;
- conservar sin modificaciones los tokens de credencial de asociados;
- escribir `EstadoDatosStaging` como último cambio transaccional;
- mantener las barreras de staging: autenticación HTTP, `noindex`, correo
  transaccional deshabilitado, correo por lote deshabilitado y push
  deshabilitado.

No se crearán automáticamente el admin QA, los asociados QA ni el comercio QA.
El comando de rotación de contraseñas QA no forma parte de este flujo.

Las sesiones no se conservan porque representan autenticaciones activas de
navegadores y no identidad persistente. La eliminación de sesiones es la única
limpieza de credenciales ejecutada por este modo.

## Riesgo aceptado y controles

Conservar hashes de contraseña y privilegios implica que las mismas
credenciales de Producción podrán autenticarse en staging. Conservar los
tokens implica que las credenciales de asociado copiadas también podrán
validarse allí.

Este riesgo se acepta explícitamente para obtener una réplica fiel. Antes de
conectar la base se deben verificar:

- que origen y destino tengan hosts, nombres, roles y huellas distintos;
- que el proyecto staging permanezca protegido y desconectado durante la copia;
- que no se configure el bucket productivo;
- que correo, correo por lote y push sigan deshabilitados;
- que no exista ninguna sesión después del endurecimiento;
- que `EstadoDatosStaging` coincida con `UNI2_PRIVATE_DATA_EPOCH`;
- que la barrera HTTP y el `noindex` estén activos antes de habilitar el acceso.

El procedimiento no debe imprimir contraseñas, tokens ni datos personales en
logs. Los accesos temporales de la operación se retiran al terminar.

## Cambios de arquitectura

### Servicio de staging

`usuarios.staging.harden_staging_clone` dejará de invalidar usuarios y de
crear cuentas sintéticas. Recibirá solamente `refresh_id`, eliminará sesiones
y escribirá el marcador dentro de una transacción.

El resultado del servicio informará la cantidad de sesiones eliminadas y que
los usuarios fueron conservados. No informará contraseñas, usernames ni
conteos de datos personales.

### Comando de management

`preparar_copia_staging` conservará la validación del entorno, del destino y del
refresh ID. Ya no exigirá las ocho variables `UNI2_STAGING_QA_*`, porque no
creará cuentas QA. Su mensaje de salida describirá la eliminación de sesiones y
la conservación de usuarios.

El nombre del comando se mantiene para no cambiar el procedimiento operativo,
pero su documentación deberá dejar claro que el modo aprobado es fiel y que
no se deben usar variables QA para este flujo.

### Copia de base

La copia PostgreSQL documentada se mantiene: destino nuevo, sin `--clean` ni
`--create`, transmisión sin dump persistente, sin owners ni privilegios del
servidor. La restauración conserva los datos de `public`, incluidos usuarios,
grupos, permisos, sesiones y perfiles; el comando posterior elimina sólo las
sesiones.

## Pruebas

Las pruebas del comando deben cubrir como mínimo:

1. Un usuario con contraseña, estado inactivo o activo, grupos, permisos,
   `staff`, `superuser` y perfil asociado queda byte a byte equivalente en los
   campos relevantes después del endurecimiento.
2. Un usuario vinculado a comercio conserva su relación y sus permisos.
3. Los hashes de contraseña no cambian y `check_password` sigue funcionando.
4. Los tokens de credencial no cambian.
5. Las sesiones copiadas se eliminan.
6. El marcador se escribe sólo cuando la transacción completa correctamente.
7. Un error revierte la eliminación de sesiones y evita escribir el marcador.
8. El comando ya no requiere variables QA ni crea cuentas QA.
9. Una confirmación de destino incorrecta no modifica usuarios ni sesiones.

Las pruebas antiguas que esperan usuarios productivos inactivos, contraseñas
inutilizables, tokens regenerados o exactamente cuatro usuarios activos deben
reemplazarse, no conservarse como expectativas alternativas.

## Documentación a actualizar

La especificación funcional y operativa debe reflejar el nuevo comportamiento
en estos archivos:

- `especificacion/casos-de-uso/cu-refrescar-staging.md`;
- `especificacion/arquitectura/refresco-staging.md`;
- `especificacion/arquitectura/staging.md`;
- `especificacion/arquitectura/glosario-deploy.md`;
- `especificacion/pruebas-manuales/staging.md`;
- `especificacion/casos-borde/cb-refresco-staging-incompleto.md`;
- `especificacion/casos-borde/cb-refresco-staging-destino-equivocado.md`;
- `especificacion/entidades/estado-datos-staging.md`, si describe la
  transacción o sus efectos.

La documentación debe indicar que no se modifican usuarios ni contraseñas,
que se eliminan sesiones y que staging contiene credenciales productivas.
También debe retirar las verificaciones de “sólo cuatro cuentas QA” de este
flujo y separar cualquier flujo QA sintético futuro de la copia fiel.

## Fuera de alcance

- No se ejecutará la copia de Producción en este cambio.
- No se modificarán las bases existentes.
- No se cambiará el modelo de usuario.
- No se implementará autenticación alternativa ni anonimización de datos.
- No se copiarán esquemas gestionados por Supabase ni el bucket productivo.
