---
type: "Alcance"
title: "Etapa de preinscripción y correo transaccional"
description: "Alcance posterior al MVP para solicitar asociación, revisar datos y habilitar los primeros correos."
tags: [post-mvp, alcance, diseno-aprobado]
timestamp: 2026-08-26T00:00:00-03:00
---

# Etapa de preinscripción y correo transaccional

Esta etapa reemplaza el inicio completamente presencial por una preinscripción
online. La revisión ocurre en Uni2 y la finalización del alta continúa siendo
presencial.

## Incluye

- Resumen `Unite a la Mutual` en la home y formulario público en página propia.
- Solicitud separada del padrón con estados `recibida`, `observada`,
  `datos_aprobados`, `alta_completada` y `cancelada`.
- Seguimiento y corrección mediante enlace privado sin crear una cuenta.
- Bandeja, filtros, ficha, historial y acciones propias en `gestion`.
- Alta atómica desde una solicitud con datos aprobados, reutilizando las reglas
  vigentes de asociados y cuotas.
- Correo transaccional individual para recepción, observación, correcciones,
  datos aprobados y cancelación.
- Infraestructura común de comunicación y entregas, con fallos visibles,
  idempotencia y reenvío.
- Permisos para consultar, revisar, completar y cancelar solicitudes asignados
  a Atención al asociado y Administrador de la mutual.

## No incluye

- Pago online o registro de un pago como condición de este flujo.
- Asociación completamente online.
- Archivos adjuntos o documentación digital.
- Autorización de una persona adulta.
- Creación de preferencias de comunicación.
- Rediseño de la creación de usuarios o del correo posterior al alta, resuelto
  posteriormente en la [etapa de acceso y autogestión](acceso-autogestion-asociado.md).
- Recuperación de contraseña mediante la nueva infraestructura, resuelta
  posteriormente en esa misma etapa.
- Avisos de cuotas generadas, comunicados institucionales o promociones.
- Procesamiento de correos por lote, colas automáticas o campañas.
- Notificaciones push, permisos o suscripciones de dispositivos.
- Anonimización o eliminación automática de solicitudes.

Los avisos obligatorios por lote, como informar cuotas generadas, y los
comunicados institucionales quedan como siguientes usos previstos de
`comunicaciones`, pero requieren diseño e implementación propios.
