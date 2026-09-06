---
type: "Entidad"
title: "SolicitudAsociacion"
description: "Preinscripción pública que puede convertirse en un asociado después de la revisión y finalización presencial."
resource: "asociados.models.SolicitudAsociacion"
tags: [post-mvp, modelo-de-datos, diseno-aprobado]
timestamp: 2026-08-26T00:00:00-03:00
---

# SolicitudAsociacion

Representa una preinscripción pública. No pertenece al padrón y no obtiene
número de asociado, credencial, cuotas ni usuario hasta que el personal
completa el alta.

**Campos:**

- id\*: identificador interno.
- clave_operacion: UUID único del envío público. El formulario nuevo lo exige y
  conserva al corregir errores; permite reconocer un reintento sin crear otra
  solicitud. NULL para solicitudes históricas o llamadas internas sin clave.
  No editable en el admin.
- nombre\*: nombre declarado por la persona.
- apellido\*: apellido declarado por la persona.
- dni\*: DNI o documento, conservado en un único campo.
- dni_normalizado\*: representación interna usada para detectar duplicados.
- email\*: correo usado como canal de contacto y para entregar el enlace privado.
- telefono\*: teléfono de contacto.
- direccion\*: domicilio declarado.
- es_estudiante_cet3\*: indica si la persona estudia en el CET 3.
- tipo\*: valor derivado: `asociado` para estudiantes del CET 3 y `adherente`
  para las demás personas.
- curso_actual: curso obligatorio cuando es estudiante del CET 3.
- clasificacion_adherente: clasificación obligatoria cuando no es estudiante
  del CET 3.
- estado\*: estado actual de la solicitud.
- token_seguimiento_hash\*: resumen seguro del último token privado emitido.
- token_seguimiento_vence_en\*: vencimiento del último enlace privado.
- asociado: asociado creado al completar el alta; queda vacío antes de ese momento.
- creado_en\*: fecha y hora de recepción.
- modificado_en\*: fecha y hora de la última modificación.
- revisado_en: fecha y hora de la última revisión del personal.
- finalizado_en: fecha y hora del alta completada o la cancelación.
- creado_por: vacío para la presentación pública.
- modificado_por: último usuario interno que modificó la solicitud; puede quedar
  vacío cuando la corrección proviene del enlace privado.

**Estados:**

- `recibida` — pendiente de revisión;
- `observada` — habilitada para corrección mediante el enlace privado;
- `datos_aprobados` — revisada y pendiente de finalización presencial;
- `alta_completada` — convertida en asociado;
- `cancelada` — cierre definitivo sin alta.

**Restricciones:**

- `dni_normalizado` no puede repetirse entre solicitudes que no estén
  canceladas ni puede coincidir con el DNI de un asociado existente.
- Una solicitud cancelada permite presentar otra con el mismo DNI.
- El correo no es único.
- Curso y clasificación son alternativos y deben coincidir con
  `es_estudiante_cet3` y `tipo`.
- `asociado` es único y solo se completa en `alta_completada`.
- El token original no se persiste; cada nueva emisión invalida el enlace anterior.
- Las solicitudes y su historial se conservan. Esta etapa no incorpora
  anonimización ni eliminación automática.

**Presentación:** apellido y nombre, seguidos por el estado.

**Orden natural e índices:** fecha de creación descendente. Índices por
`(estado, creado_en)`, `tipo`, curso y clasificación para sostener la bandeja y
sus filtros. La unicidad condicional de `dni_normalizado` cubre todos los
estados salvo `cancelada`.

**Admin técnico:** puede consultarse como apoyo, pero la revisión cotidiana se
realiza desde la pantalla propia de `gestion`.

**Referencias funcionales:** ver [reglas de solicitudes de asociación](../reglas/solicitudes-asociacion.md),
[preinscripción pública](../casos-de-uso/cu-preinscribirse-asociacion.md) y
[gestión de solicitudes](../casos-de-uso/cu-gestionar-solicitud-asociacion.md).
