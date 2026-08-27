---
type: "Entidad"
title: "EntregaComunicacion"
description: "Intento de entregar una comunicación a un destino mediante un canal."
resource: "comunicaciones.models.EntregaComunicacion"
tags: [post-mvp, modelo-de-datos, diseno-aprobado]
timestamp: 2026-08-26T00:00:00-03:00
---

# EntregaComunicacion

Representa la entrega concreta de una [Comunicación](comunicacion.md). Permite
saber qué se intentó enviar, a quién y con qué resultado.

**Campos:**

- id\*: identificador interno.
- comunicacion\*: comunicación a la que pertenece.
- canal\*: canal de salida; inicialmente `email`.
- destino\*: dirección usada para la entrega.
- estado\*: estado actual del intento.
- intentos\*: cantidad de intentos realizados.
- ultimo_intento_en: fecha y hora del último intento.
- enviado_en: fecha y hora del envío exitoso.
- proveedor_id: identificador devuelto por el proveedor cuando exista.
- ultimo_error: descripción operativa acotada del último fallo.
- creado_en\*: fecha y hora de creación.

**Estados iniciales:** `pendiente`, `enviada`, `fallida`, `omitida`.

No guarda el cuerpo completo, contraseñas ni tokens privados. Un reenvío crea
una nueva entrega y, cuando corresponde, un nuevo enlace privado. El historial
permite distinguir un mensaje nuevo de un reintento operativo.

**Presentación:** canal, destino, estado y fecha. Orden natural por creación
descendente. Índices por `(estado, creado_en)` y `(comunicacion, canal)`.

**Admin técnico:** consulta de soporte; el reenvío cotidiano se realiza desde
la ficha operativa autorizada.

**Referencias funcionales:** ver [reglas de comunicaciones](../reglas/comunicaciones.md)
y [arquitectura de comunicaciones](../arquitectura/comunicaciones.md).
