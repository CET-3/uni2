---
type: "Regla de negocio"
title: "Trazabilidad"
description: "Reglas para atribuir cambios, conservar historial y controlar bajas, anulaciones y eliminaciones."
tags: [mvp, reglas, diseno-aprobado, implementacion-parcial]
timestamp: 2026-08-09T00:00:00-03:00
---

# Trazabilidad

## Autoría

1. Toda alta o modificación realizada por una persona autenticada identifica a
   esa persona como actor.
2. Una operación automática se identifica por el nombre del proceso. No se le
   atribuye a un usuario humano ficticio.
3. La creación conserva su actor original. Las modificaciones posteriores
   actualizan solamente el responsable y fecha de última modificación.
4. Los registros anteriores a la incorporación de auditoría pueden mostrar
   autor desconocido. No se completan datos históricos por suposición.
5. Desactivar un usuario no elimina ni oculta sus eventos anteriores.
6. La etiqueta humana del actor usa nombre y apellido cuando ambos datos están
   disponibles, y el username como respaldo. La copia queda conservada en el
   evento aunque la cuenta se desactive posteriormente.

## Historial

1. Se registra un evento por cada cambio de negocio exitoso.
2. Una modificación sin cambios efectivos no genera evento.
3. Una operación que afecta varios objetos genera eventos relacionados por el
   mismo `operacion_id`.
4. Cambio y evento se confirman en la misma transacción.
5. El historial es de solo lectura para usuarios de la aplicación.
6. La auditoría conserva los datos mínimos necesarios y excluye contraseñas,
   tokens, secretos, binarios y contenido completo de archivos importados.
7. Ver la consulta general de auditoría requiere `gestion.ver_auditoria`; ver los movimientos recientes dentro de la ficha de un asociado requiere `gestion.ver_movimientos_asociado`.

## Bajas, anulaciones y eliminación

1. Editar una entidad no concede automáticamente permiso para darla de baja,
   anularla o borrarla.
2. Toda baja, anulación o eliminación física excepcional requiere un motivo
   explícito.
3. Los asociados se dan de baja mediante estado, fecha y motivo. Conservan
   cuotas, pagos y usuario vinculado.
4. Los comercios pasan al estado `baja`; no se eliminan como operación normal.
5. Los usuarios se desactivan con `is_active=False`; no se borran como operación
   normal.
6. Los pagos, aplicaciones, donaciones y cuotas no se borran para corregir una
   equivocación. La corrección financiera debe modelarse mediante una anulación
   o reversión antes de habilitarse.
7. Los períodos, categorías, productos, publicidades y otros catálogos se
   desactivan cuando el modelo ofrece un estado activo.
8. Una eliminación física se reserva para un dato técnico o de catálogo cargado
   por error, sin relaciones que deban conservarse. Solo un superusuario técnico
   puede iniciarla mediante una operación controlada.
9. La eliminación física excepcional registra previamente actor, motivo,
   entidad, identificador y representación legible del objeto.
10. Las acciones masivas de borrado no se habilitan para entidades trazables.

## Permisos iniciales

- `gestion.ver_auditoria`: consulta el historial general.
- `gestion.ver_movimientos_asociado`: consulta los últimos movimientos dentro de la ficha del asociado.
- `gestion.dar_baja_asociados`: ejecuta la baja de un asociado.
- `gestion.anular_pagos`: se utilizará cuando esté diseñado e implementado el
  flujo de anulación.

`Administrador de permisos` y `Administrador de la mutual` reciben actualmente
`gestion.ver_auditoria`. Atención al asociado y Administrador de la mutual reciben
`gestion.ver_movimientos_asociado`. Atención al asociado, Gestión de convenios y Gestión de
publicidades no reciben consulta general de auditoría ni acciones destructivas.
Los permisos de baja y anulación se asignarán cuando existan esos flujos. El
superusuario técnico conserva las tareas excepcionales de soporte, pero el admin
de Django no ofrece borrado libre de información operativa.

## Admin de Django

1. Una edición desde el admin tiene las mismas obligaciones de autoría que una
   edición desde gestión.
2. `request.user` es el actor de la operación.
3. Los campos de autoría son de solo lectura.
4. Los registros financieros son de consulta o utilizan services controlados;
   no se editan libremente mediante inlines.
5. El `LogEntry` propio de Django es una ayuda secundaria y no reemplaza
   `EventoAuditoria`.

## Importaciones y comandos

1. Una importación iniciada desde gestión identifica al usuario que subió y
   confirmó el archivo.
2. Sus eventos comparten un identificador de lote u operación.
3. El historial no copia el archivo ni filas completas; conserva conteos,
   entidades afectadas y cambios permitidos.
4. La carga inicial se identifica como comando o sistema.
5. Una migración de datos no se atribuye a la persona que posteriormente
   consulta el sistema.
6. Mientras los importadores no estén integrados con `EventoAuditoria`, las
   importaciones masivas y la creación masiva de usuarios quedan reservadas al
   superusuario `Administrador de la app`.

## Alcance implementado

Se auditan las escrituras normales de gestión y del admin: asociados, usuarios y
vinculaciones, grupos y permisos, períodos, generación de cuotas, cobros,
actividades comerciales, comercios, categorías, productos y publicidades.

Los importadores de padrón, cuotas históricas y comercios no están integrados
todavía con `EventoAuditoria`. La carga inicial y el endurecimiento de staging
siguen siendo operaciones técnicas, no acciones humanas de gestión. La anulación
de pagos permanece pendiente hasta que exista su regla y flujo funcional.
