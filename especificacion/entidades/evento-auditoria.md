---
type: "Entidad"
title: "EventoAuditoria"
description: "Hecho inmutable que identifica una operación y los cambios producidos sobre una entidad."
resource: "auditoria.models.EventoAuditoria"
tags: [mvp, modelo-de-datos, implementado]
timestamp: 2026-08-09T00:00:00-03:00
---

# EventoAuditoria

Representa un hecho exitoso y persistido sobre una entidad de Uni2. No guarda
una copia completa de cada objeto: conserva su identificación, el actor, el
origen y los campos que cambiaron.

**Campos:**

- id\*: identificador interno.
- fecha\*: fecha y hora asignada automáticamente al crear el evento.
- actor: usuario autenticado que realizó la acción. Puede quedar vacío para
  procesos automáticos o datos cuyo autor no pueda determinarse.
- actor_etiqueta\*: copia legible del nombre y apellido del usuario en el
  momento del evento. Si no tiene nombre completo cargado, usa el username; para
  una operación automática usa el nombre del proceso.
- accion\*: tipo de operación realizada.
- entidad\*: nombre técnico estable, por ejemplo `asociados.Asociado`.
- objeto_id\*: identificador del objeto convertido a texto.
- objeto_descripcion\*: representación legible del objeto en el momento de la
  operación.
- cambios\*: objeto JSON con valores anteriores y nuevos. Usa `{}` cuando la
  acción no necesita un detalle por campo.
- motivo: explicación de hasta 500 caracteres, obligatoria para bajas,
  anulaciones y eliminaciones físicas excepcionales.
- origen\*: interfaz o proceso que produjo el evento.
- operacion_id\*: UUID que permite agrupar todos los eventos de una misma
  operación.

**Acciones iniciales:**

- `crear`;
- `modificar`;
- `cambiar_estado`;
- `vincular`;
- `desvincular`;
- `anular`;
- `eliminar`.

**Orígenes iniciales:**

- `gestion`;
- `admin`;
- `importacion`;
- `comando`;
- `sistema`;
- `sitio_publico`, para una acción realizada mediante un enlace o formulario
  público sin atribuirla a un usuario Django.

**Ejemplo de cambios:**

```json
{
  "estado": {
    "anterior": "activo",
    "nuevo": "inactivo"
  },
  "fecha_baja": {
    "anterior": null,
    "nuevo": "2026-08-01"
  }
}
```

**Restricciones:**

- Un evento creado no se modifica.
- Un evento no se elimina desde las interfaces de Uni2.
- `motivo` es obligatorio para `anular` y `eliminar`.
- Una acción de baja o cambio destructivo de estado también debe tener motivo.
- Si `actor` está vacío, `actor_etiqueta` debe identificar explícitamente al
  proceso.
- No se guardan contraseñas, tokens, secretos, binarios ni planillas completas.
- El destino no usa una clave foránea genérica: `entidad`, `objeto_id` y
  `objeto_descripcion` deben sobrevivir a una eliminación excepcional.

**Presentación:**

- `__str__`: fecha, actor_etiqueta, acción y objeto_descripcion.
- orden natural: fecha descendente e id descendente.
- índices: `(entidad, objeto_id, fecha)`, `(actor, fecha)`,
  `(accion, fecha)` y `operacion_id`.

**Admin técnico:** se registra únicamente para consulta. No permite alta,
modificación ni eliminación. `actor_etiqueta` se presenta como `Nombre
registrado del actor` y explica que es una copia histórica, para diferenciarla
de la relación `Actor` con el usuario Django actual.

**Referencias funcionales:** ver
[reglas de trazabilidad](../reglas/trazabilidad.md),
[arquitectura de trazabilidad](../arquitectura/trazabilidad.md) y
[consulta de auditoría](../casos-de-uso/cu-consultar-auditoria.md).
