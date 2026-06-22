---
type: "Caso de uso"
title: "CU-ver-detalle-asociado"
description: "Actor: Gestión con permiso para consultar asociados."
tags: [mvp, caso-de-uso]
timestamp: 2026-06-22T00:00:00-03:00
---

# CU-ver-detalle-asociado

**Actor:** Gestión con permiso para consultar asociados.

**Alcance:** pantalla operativa de lectura para revisar datos, deuda y pagos recientes de un asociado antes de decidir una acción. No contiene formulario de edición.

**Flujo principal:**

1.  El usuario busca un asociado desde el listado o desde cobros.
2.  Entra al detalle.
3.  El sistema muestra datos personales, contacto, usuario vinculado, estado, curso, deuda total, cuotas del año actual y pagos recientes.
4.  Si tiene permiso de edición, puede ir a una pantalla separada para editar datos.
5.  Si tiene permiso de cobro, puede ir directo a registrar un pago.
6.  Si quiere revisar todo el historial, puede abrir la pantalla de todas las cuotas del asociado.

**Modelos afectados:** Asociado, Cuota, Pago, PagoCuota.
