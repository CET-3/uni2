---
type: "Caso de uso"
title: "CU-importar-cuotas-historicas"
description: "Actor: Administrador"
tags: [mvp, caso-de-uso]
timestamp: 2026-06-22T00:00:00-03:00
---

# CU-importar-cuotas-historicas

**Actor:** Administrador

**Alcance:** importación inicial para la puesta en marcha desde la hoja `COBRO CUOTAS SOCIALES` de la planilla heredada. No reemplaza el flujo normal de cobros.

**Flujo principal:**

1.  Sube la planilla heredada en formato `.xlsx`.
2.  El sistema lee las filas desde la fila de encabezados de cuotas sociales.
3.  El sistema identifica al asociado por `Apellido/Nombre`, usando el nombre completo normalizado (se eliminan acentos y mayúsculas). Si no encuentra coincidencia exacta, busca por apellido dentro del mismo curso (columna curso/división de la planilla).
4.  El sistema toma los meses desde marzo hasta el mes en curso de la fecha de operación, para no crear deuda futura por columnas todavía no vencidas.
5.  El sistema previsualiza cuotas a crear, pagos históricos a crear, cuotas impagas y cuotas a revisar.
6.  Si hay cuotas a revisar, el administrador puede descargar una planilla `.xlsx` agrupada en una fila por asociado/fila original, con columnas por mes para pago, forma y motivo de revisión.
7.  El administrador confirma la importación.
8.  El sistema crea períodos de cuota faltantes, cuotas, pagos históricos y aplicaciones `PagoCuota`.

**Reglas de importación:** cada período histórico se crea con vencimiento el día 10 del mes. Para marzo y abril de 2026, la cuota se crea con importe `500` y recargo `100`. Desde mayo de 2026 en adelante, la cuota se crea con importe `600` y recargo `200`. Una celda mensual verdadera genera una cuota pagada y un pago histórico por el importe de ese mes. Una celda falsa genera una cuota impaga, salvo que tenga una forma de pago cargada en la misma columna, en cuyo caso se da por pagada. La forma de pago `efectivo` se mapea a efectivo y `MP` a billetera virtual.

**Reglas de revisión:** quedan fuera de la importación automática los asociados no encontrados por nombre, los pagos marcados sin forma de pago válida, los valores de pago dudosos, las formas de pago dudosas y las cuotas ya existentes. Las filas sin `Apellido/Nombre` se descartan como filas auxiliares o incompletas para evitar falsos errores.

**Decisión funcional:** los pagos históricos importados solo crean cuotas, pagos y aplicaciones `PagoCuota`.

**Modelos afectados:** CicloLectivo, PeríodoCuota, Cuota, Pago, PagoCuota.
