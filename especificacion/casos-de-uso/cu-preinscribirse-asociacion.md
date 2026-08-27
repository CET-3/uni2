---
type: "Caso de uso"
title: "CU-preinscribirse-asociacion"
description: "Actor: Visitante que desea asociarse a UNI2."
tags: [post-mvp, caso-de-uso, diseno-aprobado]
timestamp: 2026-08-26T00:00:00-03:00
---

# CU-preinscribirse-asociacion

**Actor:** Visitante que desea asociarse a UNI2.

**Precondición:** no existe un asociado ni una solicitud no cancelada con el
mismo DNI normalizado.

**Flujo principal:**

1. Desde la sección `Unite a la Mutual` de la home abre `Comenzar preinscripción`.
2. Completa en una sola página sus datos personales y responde si estudia en el CET 3.
3. Si estudia en el CET 3 elige un curso activo; de lo contrario elige una
   clasificación de adherente activa.
4. El sistema valida y crea la solicitud como `recibida`.
5. Muestra una confirmación sin volver a exponer los datos cargados.
6. Registra una comunicación y envía el correo de recepción con un enlace
   privado de seguimiento.
7. Mediante ese enlace puede consultar el estado mientras esté vigente.
8. Si la solicitud está `observada`, ve la explicación, corrige el formulario
   y lo reenvía.
9. La solicitud vuelve a `recibida` y se confirma la recepción de las correcciones.

**Alternativas:**

- Si el DNI ya pertenece a un asociado o a otra solicitud no cancelada, no se
  crea un registro y la respuesta no revela información de la otra persona.
- Si el enlace es inválido o venció, se muestra un mensaje genérico y cómo
  contactar a la Mutual.
- Si el correo falla, la solicitud permanece recibida y el fallo queda visible
  para gestión.

**Reglas relacionadas:** [Solicitudes de asociación](../reglas/solicitudes-asociacion.md)
y [Comunicaciones](../reglas/comunicaciones.md).

**Modelos afectados:** SolicitudAsociacion, Comunicacion, EntregaComunicacion,
EventoAuditoria, Curso, ClasificacionAdherente.
