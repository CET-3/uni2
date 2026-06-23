---
type: "Arquitectura"
title: "Archivos media"
description: "Decisiones técnicas para fotos y archivos subidos."
tags: [mvp, arquitectura]
timestamp: 2026-06-23T00:00:00-03:00
---

# Archivos media

Las fotos cargadas desde el admin técnico usan campos `ImageField`.

## Local

En desarrollo local, Django guarda los archivos en `MEDIA_ROOT` y los sirve desde `MEDIA_URL` cuando `DEBUG=True`.

## Producción en Vercel

Vercel no ofrece almacenamiento persistente para archivos subidos dentro del runtime serverless. Por eso, en producción las fotos deben guardarse en un storage externo compatible con S3 mediante `django-storages`.

Variables esperadas para activar storage externo:

- `AWS_STORAGE_BUCKET_NAME`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_S3_REGION_NAME`
- `AWS_S3_ENDPOINT_URL`
- `AWS_S3_CUSTOM_DOMAIN`, opcional si el proveedor entrega dominio público propio.

Si no se configura storage externo, las fotos subidas en producción no deben considerarse persistentes.
