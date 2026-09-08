---
type: "Caso de uso"
title: "CU-crear-asociado"
description: "Actor: Gestión con permiso para editar asociados."
tags: [mvp, caso-de-uso]
timestamp: 2026-06-22T00:00:00-03:00
---

# CU-crear-asociado

**Actor:** Gestión con permiso para editar asociados.

**Alcance:** alta manual cotidiana desde `gestion/asociados/nuevo/`. No usa el admin técnico de Django.

**Flujo principal:**

1.  Carga datos personales.
2.  Selecciona el tipo. Si es `Asociado`, carga el curso; si es `Adherente`,
    elige una clasificación activa.
3.  El sistema asigna la fecha local del día como `fecha_alta`.
4.  El formulario propone la fecha local actual como `fecha_inicio_cobro`. El
    sistema calcula también la fecha automática según el tipo: dos meses antes
    para `Asociado` y el mismo mes para `Adherente`, sin usar un corte por día.
    La fecha efectiva es la más antigua entre ambas, por lo que una fecha
    anterior permite recuperar cuotas faltantes, pero una fecha reciente no
    reduce las cuotas que corresponden al alta.
5.  Guarda el asociado.
6.  Crea y vincula un usuario activo cuyo username y contraseña inicial son el
    DNI. Si el asociado tiene email, programa el correo individual de alta.
7.  El sistema genera cuotas iniciales para los períodos activos existentes
    entre `fecha_inicio_cobro` y el mes del alta. También agrega períodos
    futuros activos que ya tengan `generado_el`.
8.  El sistema informa el alta, la fecha efectiva de inicio de cobro y la
    cantidad de cuotas iniciales generadas.
9.  Siempre redirige al detalle operativo del asociado, donde la persona decide si quiere cobrar o editar.

**Reglas relacionadas:** [Asociados](../reglas/asociados.md), [Altas de asociado](../reglas/altas-de-asociado.md).

**Cancelación:** vuelve a `Atención al asociado` sin crear registros.

El formulario muestra y exige solamente el dato que corresponde al tipo. La
clasificación transitoria `Sin clasificar` no se ofrece en el alta manual.
`fecha_alta` no se muestra ni se acepta como dato editable en este flujo.
`fecha_inicio_cobro` sí se muestra y toma por defecto la fecha local actual.
Una fecha anterior se usa para recuperar cuotas faltantes desde ese mes; una
fecha igual o posterior al límite automático conserva la lógica anterior.
Ambas fechas permanecen disponibles en la edición administrativa y en el
admin técnico.

**Situaciones especiales:** DNI o username duplicado, curso inexistente,
clasificación inexistente o inactiva, email vacío, fallo del correo, períodos
faltantes o inactivos y períodos futuros creados pero todavía no generados.
El aviso informa cuando no se generaron cuotas por falta de períodos aplicables.
Reintentar la operación no duplica asociado, usuario, correo ni cuotas. Un
fallo del correo no revierte el alta.

**Modelos afectados:** Asociado, User, Curso, ClasificacionAdherente,
PeríodoCuota, Cuota, Comunicacion y EntregaComunicacion.
