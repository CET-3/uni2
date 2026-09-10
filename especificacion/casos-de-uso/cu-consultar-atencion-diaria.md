---
type: "Caso de uso"
title: "CU-consultar-atencion-diaria"
description: "Controlar cobros, altas y solicitudes pendientes."
tags: [gestion, caso-de-uso, pagos]
timestamp: 2026-09-10T00:00:00-03:00
---

# CU-consultar-atencion-diaria

**Actor:** persona con `gestion.ver_atencion_diaria`.

**Flujo principal:**

1. Abre `Atención diaria` desde los accesos administrativos de la home.
2. Consulta los ingresos de hoy por medio de pago y su composición.
3. Puede elegir ayer, lunes a hoy o un rango de fechas. Si tiene permiso para
   cobros del equipo puede alternarlos con sus propios cobros.
4. Recorre los pagos y abre uno para revisar fecha, operador, cuotas cubiertas y
   donaciones. Los breadcrumbs conservan los filtros para regresar al tablero.
5. Si aparece un aviso de fechas de carga distintas, abre el listado y revisa
   ambos datos. No modifica el pago desde esta pantalla.
6. Con permisos de consulta de asociados puede ver las altas del rango y
   continuar en la ficha existente. Con permisos de solicitudes puede abrir
   las bandejas pendientes por estado.

**Situaciones especiales:** período sin pagos, filtros inválidos, pagos sin
operador, falta de fecha de carga auditada, aplicaciones inconsistentes,
importaciones con fecha convencional y acceso a un pago ajeno no autorizado.

**Reglas relacionadas:** [Atención diaria](../reglas/atencion-diaria.md).
**Pantalla:** [Atención diaria](../pantallas/atencion-diaria.md).
