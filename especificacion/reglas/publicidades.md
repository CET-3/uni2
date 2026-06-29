---
type: "Regla de negocio"
title: "Publicidades"
description: "Reglas de negocio sobre publicidades destacadas en la home."
tags: [mvp, reglas]
timestamp: 2026-06-23T00:00:00-03:00
---

# Publicidades

## PUBLICIDAD-001

La home muestra solamente publicidades activas, ordenadas por `orden` y luego por `título`. Si una publicidad está vinculada a un comercio, solo se muestra si ese comercio tiene estado `Firmado`.

## PUBLICIDAD-002

Una publicidad puede vincularse a un producto o servicio, o a un comercio, pero no a ambos al mismo tiempo.

## PUBLICIDAD-003

Si la publicidad tiene un producto o servicio vinculado, el enlace lleva al detalle público de ese producto o servicio. Si tiene un comercio vinculado, el enlace lleva al detalle público de ese comercio. Si no tiene vínculo, se muestra sin enlace.

## PUBLICIDAD-004

Las fotos de publicidades deben seguir el formato recomendado documentado en la entidad `Publicidad`: horizontal 16:9, WebP o JPG, contenido principal centrado y peso ideal menor a 500 KB.

Si una publicidad activa no tiene foto cargada, la home debe mostrar la card sin imagen de fondo y sin romper la página.

## PUBLICIDAD-005

En el MVP, la carga y edición de publicidades se realiza desde el admin técnico de Django.
