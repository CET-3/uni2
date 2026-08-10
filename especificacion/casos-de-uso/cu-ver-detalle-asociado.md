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

1.  El usuario busca un asociado desde `Atención al asociado`.
2.  Entra al detalle.
3.  El sistema muestra datos personales, contacto, usuario vinculado, estado, curso, deuda total, cuotas del año actual y pagos recientes.
4.  Si tiene permiso de edición, puede elegir `Editar asociado`.
5.  Si tiene permiso de cobro, puede elegir `Cobrar`.
6.  Una navegación secundaria permite volver a `Atención al asociado` y conserva los filtros de la búsqueda de origen mediante un parámetro local validado.
7.  Si tiene permiso `gestion.ver_movimientos_asociado`, al pie ve las diez operaciones de auditoría más recientes relacionadas con el asociado.
8.  Si además tiene `gestion.ver_auditoria`, puede abrir el historial completo filtrado.

**Acciones principales:** el encabezado contiene únicamente `Editar asociado` y `Cobrar`, sujetas a permisos. La auditoría es información secundaria al pie y no agrega una acción al encabezado. El historial completo de cuotas y la creación individual de usuario no tienen acceso desde esta pantalla mientras se diseñan sus recorridos definitivos.

**Modelos afectados:** Asociado, Cuota, Pago, PagoCuota.
