---
type: "Caso de uso"
title: "CU-consultar-deudores"
description: "Actor: Gestión con permiso para consultar deudores."
tags: [mvp, caso-de-uso, asociados, cuotas]
timestamp: 2026-08-10T00:00:00-03:00
---

# CU-consultar-deudores

**Actor:** Gestión con permiso `gestion.ver_deudores`.

**Alcance:** listado operativo de asociados con deuda. La ruta se conserva para
acceso explícito, pero la home no muestra un botón `Ver deudores`.

**Flujo principal:**

1. La persona autorizada abre el listado de deudores.
2. El sistema identifica asociados con cuotas pendientes o vencidas.
3. Muestra la deuda calculada para cada asociado.
4. La persona usa esa información para organizar el seguimiento y continúa la
   operación desde las pantallas habilitadas.

**Situaciones especiales:** ningún asociado con deuda, cuotas parcialmente
pagadas, asociado inactivo y usuario sin permiso.

**Modelos afectados:** Asociado, Cuota, Pago y PagoCuota.

**Reglas relacionadas:** [Cuotas](../reglas/cuotas.md).
