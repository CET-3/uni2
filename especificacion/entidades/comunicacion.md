---
type: "Entidad"
title: "Comunicacion"
description: "Mensaje originado por un hecho de negocio y agrupador de sus entregas por canal."
resource: "comunicaciones.models.Comunicacion"
tags: [post-mvp, modelo-de-datos, diseno-aprobado]
timestamp: 2026-08-26T00:00:00-03:00
---

# Comunicacion

Representa el mensaje lógico originado por un hecho de negocio. Separa el
motivo de comunicar de cada intento concreto de entrega.

**Campos:**

- id\*: identificador interno.
- tipo\*: código estable, por ejemplo `preinscripcion_observada` o, en una
  etapa futura, `cuotas_generadas`.
- alcance\*: `individual` o `lote`.
- clave_idempotencia\*: clave única que impide crear dos veces la misma
  comunicación para una misma operación.
- origen_entidad\*: nombre técnico de la entidad que produjo el mensaje.
- origen_id\*: identificador del objeto de origen.
- creado_en\*: fecha y hora de creación.
- creado_por: usuario que inició la comunicación cuando corresponde.

Una comunicación individual tendrá normalmente una entrega. Una comunicación
por lote podrá agrupar muchas entregas y procesarlas en tandas. La primera
etapa implementa solamente comunicaciones individuales de preinscripción.

No guarda contraseñas, tokens privados ni una copia completa de los datos de
negocio. Las plantillas se versionan en el repositorio.

**Presentación:** tipo, alcance y fecha. Orden natural por creación descendente.
`clave_idempotencia` es única y el origen tiene un índice compuesto por entidad
e identificador.

**Admin técnico:** consulta de soporte; la creación ocurre mediante services.

**Referencias funcionales:** ver [reglas de comunicaciones](../reglas/comunicaciones.md)
y [arquitectura de comunicaciones](../arquitectura/comunicaciones.md).
