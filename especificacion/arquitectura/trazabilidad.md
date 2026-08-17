---
type: "Arquitectura"
title: "Trazabilidad y auditoría"
description: "Diseño técnico aprobado para identificar autores, conservar cambios y controlar operaciones destructivas."
tags: [mvp, arquitectura, diseno-aprobado, implementacion-parcial]
timestamp: 2026-08-09T00:00:00-03:00
---

# Trazabilidad y auditoría

## Estado

La infraestructura de eventos, la consulta web y la auditoría de las escrituras
normales del MVP están implementadas. La implementación actual cubre altas y
modificaciones de asociados desde gestión; creación de usuarios y vinculaciones;
períodos y generación de cuotas; cobros y sus pagos, aplicaciones, cuotas y
donaciones relacionadas; y CRUD simples realizados desde el admin de Django.

Los importadores de padrón, cuotas históricas y comercios quedan expresamente
fuera de esta etapa. Tampoco existe todavía el flujo funcional de anulación de
pagos. `ModeloTrazable` está disponible como base abstracta, pero los campos de
autoría actual todavía no fueron incorporados a todos los modelos operativos.

## Objetivo

Uni2 debe poder responder, como mínimo:

- quién creó un registro;
- cuándo fue creado;
- quién lo modificó por última vez;
- cuándo fue modificado por última vez;
- qué campos cambiaron, con su valor anterior y nuevo cuando sea seguro
  conservarlos;
- desde dónde se realizó la operación;
- qué cambios pertenecieron a una misma operación o importación;
- quién estaba autorizado para dar una baja, anular o realizar una eliminación
  física excepcional.

La auditoría complementa los permisos, pero no los reemplaza. Primero se valida
que una persona pueda realizar una acción; después se ejecutan el cambio y su
registro de auditoría.

## Dos capas complementarias

### Estado actual de autoría

Los modelos operativos propios de Uni2 podrán heredar un modelo abstracto
`ModeloTrazable` con estos campos:

- `creado_en`;
- `creado_por`;
- `modificado_en`;
- `modificado_por`.

El modelo será abstracto: no tendrá una tabla propia. Django agregará estos
cuatro campos a la tabla de cada modelo que lo herede.

Los campos de usuario aceptarán `NULL` para representar datos anteriores a la
auditoría y procesos automáticos sin una cuenta humana. Las pantallas mostrarán
esos casos como `No registrado` o con la identificación explícita del proceso,
nunca atribuyéndolos a una persona supuesta.

`creado_por` no se modifica después del alta. `modificado_por` se actualiza en
cada modificación real. Los cuatro campos son de solo lectura en formularios y
en el admin.

Esta capa permite responder rápidamente por el estado actual, pero no conserva
por sí sola todas las versiones anteriores.

### Historial de eventos

La app nueva `auditoria` tendrá el modelo persistente
`EventoAuditoria`. Cada fila representa un hecho ya ocurrido: creación,
modificación, cambio de estado, anulación o eliminación física excepcional.

El evento conserva una identificación textual del modelo y del objeto, en lugar
de una relación rígida con todas las entidades de negocio. Así el historial
sigue siendo legible aunque el objeto haya sido eliminado excepcionalmente o
el modelo cambie en una migración futura.

La definición funcional completa está en
[EventoAuditoria](../entidades/evento-auditoria.md).

## Organización del código

La app se organizará así:

```text
auditoria/
├── admin.py       # consulta técnica de eventos, siempre de solo lectura
├── apps.py
├── models.py      # ModeloTrazable y EventoAuditoria
├── selectors.py   # búsquedas del historial
├── services.py    # creación explícita y serialización segura de eventos
├── migrations/
└── tests/
```

Las responsabilidades quedan separadas de esta manera:

- los modelos persisten el estado actual y el evento;
- los services de cada dominio ejecutan las reglas de negocio;
- `auditoria.services` recibe los datos ya identificados por esos services y
  guarda el evento;
- los selectors consultan y ordenan el historial;
- las views solamente pasan `request.user` como actor y presentan el resultado;
- el admin obtiene el actor desde `request.user`, pero no implementa reglas de
  negocio sensibles.

## Registro explícito desde services

No se utilizarán signals como mecanismo principal de auditoría. Un signal puede
detectar que ocurrió un `save()`, pero no conoce con claridad el motivo de
negocio, el origen, el lote de importación ni la operación completa. Además,
las escrituras con `QuerySet.update()`, importaciones o SQL directo pueden
evitarlo.

La interfaz esperada de un servicio de negocio será explícita:

```python
actualizar_asociado(
    asociado=asociado,
    datos=form.cleaned_data,
    actor=request.user,
    origen=EventoAuditoria.ORIGEN_GESTION,
)
```

Dentro de una única `transaction.atomic()` el servicio:

1. valida permisos y reglas que le correspondan;
2. obtiene los valores anteriores;
3. modifica el objeto;
4. actualiza `modificado_por`;
5. guarda el objeto;
6. crea uno o más eventos de auditoría con el mismo `operacion_id`.

Si falla el cambio o falla la creación del evento, la transacción completa se
revierte. No debe confirmarse una modificación relevante sin su evento.

Los intentos rechazados y los errores que no cambian datos no se guardarán como
`EventoAuditoria` en la primera etapa. Esos casos pertenecen a un futuro
registro de seguridad y observabilidad.

## Identificación del actor

Los services recibirán:

- `actor`: instancia de `User` cuando actuó una persona autenticada;
- `actor_etiqueta`: copia legible del username o identificación del proceso;
- `origen`: pantalla de gestión, admin, importación, comando o sistema.

Para acciones humanas, `actor` es obligatorio. Para procesos automáticos puede
ser `None`, pero `actor_etiqueta` debe explicar el proceso, por ejemplo
`Sistema: generación de cuotas`.

La etiqueta se conserva aunque la cuenta sea posteriormente desactivada. Los
usuarios no deben borrarse como operación habitual: se desactivan mediante
`is_active=False`.

## Operaciones compuestas

Una sola acción puede modificar varios objetos. `operacion_id` agrupa todos los
eventos de esa acción.

Por ejemplo, registrar un pago puede:

- crear un `Pago`;
- crear uno o más `PagoCuota`;
- actualizar una o más `Cuota`;
- crear una `Donacion`.

Todos esos eventos compartirán el mismo `operacion_id`. La interfaz los
presenta dentro de una sola tarjeta de operación, sin desplegables y sin perder
el detalle de ninguna fila. Los filtros primero identifican operaciones por sus
eventos coincidentes y luego el selector recupera todos los eventos de cada
operación. La paginación se realiza sobre operaciones para no dividir sus
eventos entre páginas. Esta composición pertenece a `auditoria.selectors`; la
vista solamente pagina los resultados y el template los representa.

En una importación, todas las filas compartirán además el mismo identificador de
operación o lote. Cada fila se confirmará en una transacción independiente
cuando el importador admita continuar después de un error. Al finalizar podrá
registrarse un evento resumen con cantidad de altas, modificaciones y errores,
sin copiar el contenido completo de la planilla.

## Representación de cambios

`cambios` utilizará un objeto JSON con nombres explícitos:

```json
{
  "telefono": {
    "anterior": "1234",
    "nuevo": "5678"
  },
  "curso_actual": {
    "anterior": {"id": 4, "texto": "2do 1ra CB TM"},
    "nuevo": {"id": 9, "texto": "3ro 1ra CB TM"}
  }
}
```

La serialización seguirá estas reglas:

- fechas y horas en formato ISO 8601;
- decimales como texto para no perder precisión;
- relaciones mediante identificador y representación legible;
- archivos mediante nombre o ruta relativa, nunca copiando su contenido;
- `None`, booleanos, números y texto mediante valores JSON simples;
- no registrar un evento de modificación cuando no cambió ningún campo de
  negocio.

Cada dominio definirá una lista explícita de campos auditables. No se serializará
automáticamente todo `model_to_dict()`, porque podría incorporar nuevos campos
sensibles sin revisión.

Nunca se guardarán en `cambios`:

- contraseñas ni hashes de contraseña;
- tokens de credencial;
- secretos, claves o cookies;
- contenido binario;
- contenido completo de planillas importadas.

Los datos personales necesarios para explicar una operación, como cambios de
DNI o contacto, solo serán visibles para personas con permiso de auditoría.
Cada incorporación de un campo sensible debe revisarse antes de agregarlo a la
lista auditable.

## Integración con el admin de Django

Django crea entradas `LogEntry` para parte de las operaciones hechas desde su
admin. Ese registro se mantiene como ayuda técnica, pero no es la fuente de
verdad de Uni2 porque no cubre las pantallas de gestión, services, importadores
ni procesos automáticos.

Para catálogos con edición CRUD simple se usa `AuditoriaAdminMixin`. El mixin
captura el estado persistido antes de guardar y registra el evento después de
`save_related()`, para incluir también relaciones muchos a muchos como grupos y
permisos. Su flujo:

1. obtiene el objeto anterior cuando existe;
2. toma los campos modificados desde `form.changed_data`;
3. deja que el `ModelAdmin` guarde el objeto y sus relaciones;
4. registra el evento con origen `admin` y el usuario de la request como actor.

`ModeloTrazable` define campos de autoría reutilizables, pero todavía no fue
incorporado a los modelos de negocio. En la implementación actual la fuente de
autoría es `EventoAuditoria`; el mixin no supone que el modelo tenga campos
`creado_por` o `modificado_por`.

Para acciones sensibles, el admin no duplicará la regla: utilizará el mismo
service que la pantalla de gestión o quedará como consulta de solo lectura. Hay
que revisar además:

- `save_formset()` para inlines;
- `save_related()` para relaciones muchos a muchos;
- `delete_model()` para una eliminación individual excepcional;
- `delete_queryset()` y la acción `delete_selected` para eliminaciones masivas;
- acciones personalizadas del admin.

En particular, `Pago`, `PagoCuota`, `Donacion` y las cuotas ya afectadas por un
cobro no deben poder editarse o borrarse libremente desde el admin. Durante la
primera etapa se debe bloquear su eliminación y dejar la anulación para una
acción de negocio documentada.

## Escrituras que deben revisarse

Antes de considerar completa la implementación hay que inventariar y adaptar:

- `form.save()` en views de gestión;
- `objects.create()`, `get_or_create()`, `update_or_create()` y `save()` en
  services;
- importadores de asociados, comercios y cuotas históricas;
- creación y vinculación de usuarios;
- comandos de carga inicial;
- formularios e inlines del admin;
- cualquier `QuerySet.update()` o eliminación masiva.

Las escrituras automáticas deben identificar su origen. No se debe inventar un
usuario humano para la carga inicial, una migración o una tarea del sistema.

## Borrado y conservación

La política funcional se detalla en
[Trazabilidad](../reglas/trazabilidad.md). Técnicamente:

- las entidades operativas usan baja, desactivación o anulación;
- el botón y la acción masiva de borrado se quitan del admin para esas
  entidades;
- una eliminación física excepcional requiere un service específico, permiso,
  motivo y evento previo con una copia legible del objeto;
- el evento no usa una clave foránea al objeto eliminado, por lo que sobrevive;
- el acceso directo a la base de datos queda fuera de la trazabilidad de la app
  y debe limitarse mediante controles de infraestructura, respaldos y acceso
  restringido.

Como excepción acotada para depurar la carga inicial en desarrollo, staging y
producción, el admin permite al superusuario eliminar `Curso`, `Asociado`,
`PeriodoCuota` y `User`, tanto individualmente como mediante
`delete_selected`. La confirmación incluye las cascadas aunque los modelos
financieros relacionados mantengan bloqueado su borrado directo. Los períodos
referenciados por cuotas conservan `PROTECT` y no pueden eliminarse. Esta
limpieza no genera un `EventoAuditoria` de Uni2; conserva solamente el registro
técnico estándar del admin de Django.

## Inmutabilidad

`EventoAuditoria` será de solo agregado a nivel de aplicación:

- no habrá services de actualización o eliminación;
- el admin no ofrecerá alta, edición ni borrado;
- la pantalla de gestión será de solo lectura;
- el modelo rechazará cambios sobre una instancia ya creada;
- los tests verificarán que las rutas normales no permitan modificar ni borrar
  eventos.

SQLite no permite aplicar los mismos controles de permisos de base de datos que
PostgreSQL. En producción podrá agregarse, como endurecimiento posterior, un
usuario de base con privilegios limitados o reglas específicas. La primera
implementación no dependerá de triggers para seguir siendo fácil de ejecutar y
enseñar en los entornos de alumnos.

## Datos existentes

La auditoría no puede reconstruir quién creó o modificó datos anteriores a su
instalación.

La migración:

- agregará campos de actor permitiendo `NULL`;
- identificará fechas incorporadas por la migración como adopción del sistema de
  trazabilidad, no como prueba de la creación histórica;
- no inventará autores;
- comenzará a crear eventos solamente para operaciones nuevas.

La interfaz mostrará `No registrado: dato anterior a la auditoría` cuando
corresponda.

## Permisos previstos

El permiso implementado es:

- `gestion.ver_auditoria`;
- `gestion.ver_movimientos_asociado`;

Quedan previstos para sus flujos futuros:

- `gestion.dar_baja_asociados`;
- `gestion.anular_pagos`.

El permiso de edición no concede automáticamente baja, anulación ni borrado.
Inicialmente:

- Administrador de permisos y Administrador de la mutual reciben
  `gestion.ver_auditoria` para la consulta completa;
- Atención al asociado y Administrador de la mutual reciben
  `gestion.ver_movimientos_asociado` para el historial de la ficha;
- Atención al asociado, Gestión de convenios y Gestión de publicidades no
  reciben `ver_auditoria` ni acciones destructivas;
- `auditoria.view_eventoauditoria` controla la consulta en el admin técnico,
  mientras `gestion.ver_auditoria` controla la pantalla propia de gestión;
- el borrado físico excepcional queda reservado al superusuario técnico y no se
  presenta como una tarea normal de gestión.

Ambos permisos de lectura están registrados en `gestion/permissions.py`, en el
modelo técnico `PermisoGestion`, en las migraciones de grupos y en las pruebas.
Los permisos de baja y anulación se agregarán cuando se implementen sus operaciones.

## Pantallas previstas

La consulta global se define en
[Auditoría de gestión](../pantallas/auditoria.md) y su flujo en
[CU-consultar-auditoria](../casos-de-uso/cu-consultar-auditoria.md).

Además, el detalle de entidades importantes podrá incluir una sección
`Historial` filtrada por `entidad` y `objeto_id`.

## Plan de implementación

### Etapa 1: infraestructura — implementada

1. Crear la app `auditoria` y registrarla en `INSTALLED_APPS`.
2. Implementar `ModeloTrazable` y `EventoAuditoria`.
3. Crear la migración y revisar índices.
4. Implementar `registrar_evento()` y serializadores seguros.
5. Registrar `EventoAuditoria` en el admin como solo lectura.
6. Agregar pruebas del modelo, serialización, inmutabilidad y transacciones.

**Resultado verificable:** es posible crear y consultar eventos desde un test,
pero todavía no se modificaron todos los dominios.

### Etapa 2: asociados — parcial

1. Incorporar campos trazables a `Asociado`.
2. Cambiar `create_asociado()` para recibir actor y origen.
3. Crear o consolidar un service de modificación de asociado.
4. Cambiar `dar_baja_asociado()` para exigir actor y motivo no vacío.
5. Adaptar las views que actualmente usan `form.save()`.
6. Adaptar la creación y vinculación de usuarios de asociados.
7. Adaptar la importación de padrón con identificación de lote y actor.
8. Cubrir el admin de asociados y bloquear el borrado.
9. Agregar tests de alta, edición, baja, vinculación e importación.

**Resultado verificable:** se puede reconstruir la historia de un asociado
creado o modificado después de esta etapa, desde gestión o desde el admin.

### Etapa 3: cuotas y pagos — parcial

1. Auditar generación y modificación de períodos de cuota.
2. Hacer que `registrar_pago()` comparta un `operacion_id` entre pago,
   aplicaciones, cuotas y donación.
3. Bloquear edición y eliminación insegura en los admins financieros.
4. Definir antes de implementarla la entidad o los campos necesarios para
   anulación de pagos; no simular una anulación mediante borrado.
5. Adaptar la importación de cuotas históricas.
6. Agregar pruebas de atomicidad y agrupación de eventos.

**Resultado verificable:** cada cobro explica quién lo registró y todos los
cambios contables simples que produjo.

### Etapa 4: comercios, contenidos y catálogos — parcial

1. Incorporar trazabilidad a comercios, actividades, productos, categorías y
   publicidades.
2. Adaptar importadores y carga inicial.
3. Aplicar el mixin de admin solamente en CRUD simples.
4. Usar estados `activo` o `baja` antes que eliminación física.
5. Agregar pruebas de admin, services e importación.

### Etapa 5: usuarios, permisos y consulta — implementada

1. Auditar creación, vinculación, cambio de grupos, permisos y desactivación de
   usuarios sin registrar contraseñas.
2. Crear los permisos previstos y asignarlos a los grupos definidos.
3. Implementar selectors con filtros y paginación.
4. Implementar `/gestion/auditoria/`.
5. Incorporar el historial contextual en los detalles prioritarios.
6. Agregar pruebas de 403, filtros, privacidad y solo lectura.

## Pruebas mínimas de aceptación

- Un alta desde gestión registra actor, origen, objeto y acción.
- Una edición registra solamente los campos que realmente cambiaron.
- Un alta o edición desde el admin registra `request.user`.
- Los campos `creado_por` y `modificado_por` no pueden elegirse manualmente.
- Una importación identifica actor y lote sin copiar la planilla.
- Una operación de pago agrupa todos sus eventos.
- Un error dentro de la operación revierte cambio y auditoría.
- Un usuario sin permiso recibe 403 al consultar auditoría.
- Un usuario con permiso puede filtrar por actor, fecha, entidad y acción.
- Las contraseñas y tokens nunca aparecen en `cambios`.
- Los eventos no pueden editarse ni borrarse desde gestión o admin.
- Asociados, usuarios y registros financieros no ofrecen borrado físico normal.
- Los registros anteriores muestran autor desconocido sin inventar datos.

## Cobertura implementada

- Una alta o edición de asociado desde gestión registra actor y cambios.
- La creación y vinculación de un usuario comparte un `operacion_id`.
- La creación de períodos y la generación de cuotas identifican al actor o al
  proceso automático.
- Un cobro agrupa mediante `operacion_id` los eventos de `Pago`, `PagoCuota`,
  `Cuota` y `Donacion`.
- El admin audita asociados, ciclos, cursos, períodos, actividades comerciales,
  comercios, categorías, productos, publicidades, usuarios, grupos y permisos.
- Cuotas, pagos, aplicaciones y donaciones son de solo lectura en el admin.
- Las contraseñas no forman parte de las listas de campos auditables.
- La consulta `/gestion/auditoria/` requiere permiso, permite filtros y ofrece
  acceso contextual desde el detalle de asociado.

## Riesgos y decisiones pendientes

- Antes de la etapa financiera hay que diseñar la anulación de pagos y su efecto
  sobre cuotas y donaciones.
- El volumen del historial debe medirse antes de definir una política de
  retención. No se eliminarán eventos automáticamente en el MVP.
- Las escrituras directas por SQL no pueden identificar actor de aplicación; el
  acceso a producción debe ser excepcional y documentado.
- Los cambios de relaciones muchos a muchos requieren tratamiento explícito;
  no quedan cubiertos solamente por `save_model()`.
- Debe revisarse cada nuevo campo personal antes de incluir sus valores
  anteriores en el historial.
