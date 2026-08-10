---
type: "Proceso"
title: "Convenios, productos y publicidades"
description: "Tres procesos independientes para mantener la oferta pública de Uni2."
tags: [mvp, procesos, comercios, contenidos]
timestamp: 2026-08-10T00:00:00-03:00
---

# Convenios, productos y publicidades

Estos procesos se relacionan en el sitio público, pero tienen responsables y
permisos separados. Quien necesite participar en más de uno recibe más de un
grupo.

## Gestión de convenios

**Responsable:** grupo `Gestión de convenios`.

Registra actividades comerciales, datos del comercio, beneficio, vigencia y
estado del convenio. El resultado es un comercio adherido listo para su
publicación y para la validación de credenciales. No modifica productos,
publicidades, asociados ni usuarios.

**Caso de uso:** [administrar convenios](../casos-de-uso/cu-administrar-convenios.md).

## Gestión de productos y servicios

**Responsable:** grupo `Gestión de productos y servicios`.

Mantiene categorías, productos, servicios, descripción, precios, orden y
visibilidad. El resultado es el catálogo que consume el sitio público. No crea
publicidades ni modifica comercios.

**Caso de uso:** [administrar productos y servicios](../casos-de-uso/cu-administrar-productos-servicios.md).

## Gestión de publicidades

**Responsable:** grupo `Gestión de publicidades`.

Crea y modifica piezas publicitarias y puede consultar comercios y productos
para vincularlas. Esa consulta no autoriza a modificar el objeto vinculado. El
resultado es una publicidad configurada para su período y ubicación.

**Caso de uso:** [administrar publicidades](../casos-de-uso/cu-administrar-publicidades.md).

## Pruebas mínimas de separación

- Cada perfil puede agregar y modificar solamente objetos de su dominio.
- Publicidades puede seleccionar un comercio o producto existente, pero no
  editarlo.
- Productos y servicios no puede crear una publicidad.
- Convenios no puede modificar contenidos.
- Una cuenta con los tres grupos puede completar el recorrido integrado.
