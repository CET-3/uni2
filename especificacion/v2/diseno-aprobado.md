---
type: "Diseño futuro"
title: "Diseño aprobado para Versión 2"
description: "Definiciones aprobadas que quedan fuera del MVP."
tags: [v2, fuera-del-mvp]
timestamp: 2026-06-22T00:00:00-03:00
---

# Diseño aprobado para Versión 2

Esta sección reúne definiciones ya acordadas que quedan fuera del MVP, pero forman parte del diseño aprobado para una segunda versión.

### Alcance V2

- Productos.
- Variantes.
- Pedidos.
- Items de pedido.
- Pagos de pedidos.
- Movimiento de stock.
- Pantalla propia de gestión de productos y servicios en backoffice.
- Pantalla propia de gestión de comercios en backoffice.
- Pantalla propia de gestión de actividades comerciales en backoffice.
- Reportes de ventas y stock.
- Dashboards con métricas, alertas y reportes agregados.
- Importación regular de asociados en formato Uni2 normalizado.

### Modelo de datos V2

**Entidades V2:** Producto, VarianteProducto, MovimientoStock, Pedido, ItemPedido, PagoPedido, Notificación, BeneficioComercio.

Los atributos marcados con **\*** son obligatorios: deben tener valor, ya sea cargado por una persona o definido automáticamente por el sistema.

### Dashboards e ideas futuras

Las métricas y tableros agregados se guardan como idea futura para no complejizar el MVP.

- Resumen de asociados activos e inactivos.
- Asociados por curso y por tipo.
- Asociados con usuario y sin usuario.
- Ultimos accesos.
- Altas y bajas por mes.
- Cuotas generadas, pagadas, pendientes y vencidas.
- Deudores prioritarios y deudores por curso.
- Recaudacion por período y por método de pago.
- Comercios adheridos y beneficios vigentes.
- Alertas rápidas para tareas pendientes.

### Producto

**Campos sugeridos:**

- id\*
- nombre\*
- descripción
- precio\*
- activo
- controla_stock

**Ejemplos:** Remera Uni2, Apunte Matemática, Cuadernillo Inglés.

### VarianteProducto

**Campos sugeridos:**

- id\*
- producto\*
- nombre\*
- sku
- activo

**Ejemplos:** Talle S, M, L, XL para Remera Uni2; variante unica para apuntes.

### MovimientoStock

**Campos sugeridos:**

- id\*
- variante\*
- tipo\*
- cantidad\*
- fecha\*
- descripción

**Tipos:** ingreso, egreso, ajuste, devolucion.

**Decision:** el stock se descuenta al entregar el pedido, no al crearlo ni al pagarlo.

### Pedido

**Campos sugeridos:**

- id\*
- asociado\*
- fecha\*
- estado\*
- estado_pago\*
- total\*
- observaciones

**Estados:** pendiente, en_preparacion, entregado, cancelado.

**Estados de pago:** pendiente, pagado.

**Decisiones:** no se permiten pagos parciales en V2 inicial, no se entregan pedidos impagos y no se cancelan pedidos entregados.

### ItemPedido

**Campos sugeridos:**

- id\*
- pedido\*
- variante\*
- cantidad\*
- precio_unitario\*
- subtotal\*

### PagoPedido

**Campos sugeridos:**

- id\*
- pago\*
- pedido\*
- importe\*

**Relación futura:** Pago 1 - N PagoCuota y Pago 1 - N PagoPedido.

**Decision:** se conserva un único modelo Pago para ingresos; PagoCuota explica cuotas y PagoPedido explica pedidos.

### BeneficioComercio

Entidad futura para modelar múltiples beneficios por comercio o promociones con mayor complejidad.

**Campos sugeridos:**

- id\*
- comercio\*
- titulo\*
- descripcion\*
- tipo_descuento\*
- valor_descuento\*
- condiciones
- fecha_desde\*
- fecha_hasta
- activo

### Notificación

Notificación interna del sistema.

**Campos sugeridos:**

- id\*
- usuario\*
- título\*
- mensaje\*
- leída
- fecha_creación

**Notas:** puede usarse como notificación interna; las push quedan para una versión futura.

### Reglas V2

- RV2-001 No se permite crear pedido si no hay stock suficiente.
- RV2-002 El stock se descuenta al entregar el pedido.
- RV2-003 No se puede entregar un pedido impago.
- RV2-004 No se permite pago parcial de pedidos en V2 inicial.
- RV2-005 No se puede cancelar un pedido entregado.
- RV2-006 Algunos productos pueden no controlar stock.

### Casos de uso V2

- CU-V2-001 Crear pedido.
- CU-V2-002 Registrar pago de pedido.
- CU-V2-003 Entregar pedido.
- CU-V2-004 Ver estado de pedidos.
- CU-V2-005 Gestionar comercio desde pantalla propia de backoffice.
- CU-V2-006 Gestionar actividad comercial desde pantalla propia de backoffice.
- CU-V2-007 Gestionar beneficio desde pantalla propia de backoffice.
- CU-importar-asociados-formato-uni2.

### CU-importar-asociados-formato-uni2

**Actor:** Administrador

**Alcance:** caso de uso futuro para mantenimiento regular del padrón después de la puesta en marcha. No forma parte del MVP.

**Flujo esperado:**

1.  El administrador sube una planilla `.xlsx` con el formato Uni2 normalizado.
2.  El sistema valida columnas, tipos, DNI, número de asociado, fechas, estado y curso.
3.  El sistema previsualiza altas, actualizaciones, filas a revisar y cursos nuevos que se crearían.
4.  El administrador confirma la importación.
5.  El sistema guarda solo las filas válidas o confirmadas, según las reglas definidas para esa versión.

**Decisión funcional:** este importador no debe deducir apellido, nombre, ciclo, año, división o turno desde textos libres. Si esos datos faltan o no coinciden con los valores esperados, la fila debe quedar para revisar.

**Relación con la exportación:** debe aceptar el mismo formato generado por [CU-exportar-asociados-formato-uni2](../casos-de-uso/cu-exportar-asociados-formato-uni2.md), que ya está definido para el MVP.

**Modelos afectados:** Asociado, Curso.

### Casos borde V2

- Pedido sin stock suficiente.
- Intento de entregar pedido impago.
- Intento de cancelar pedido ya entregado.
- Producto que no controla stock.

### Reportes V2

- Pedidos pendientes.
- Pedidos pagados.
- Pedidos entregados.
- Ventas por producto.
- Stock actual.
- Movimientos de stock.
