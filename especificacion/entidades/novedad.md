---
type: "Entidad"
title: "Novedad"
description: "Publicación breve visible en la home y desarrollada en una ficha pública."
resource: "contenidos.models.Novedad"
tags: [mvp, entidad, contenidos]
---

# Novedad

Representa una noticia, actividad o evento que la mutual comunica en el sitio público. Se administra desde el admin técnico de Django durante el MVP.

## Campos

| Campo | Obligatorio | Descripción |
|---|---:|---|
| `titulo` | * | Nombre visible de la novedad. |
| `slug` | * | Identificador único usado en la URL pública. |
| `etiqueta` | * | Categoría breve mostrada en las tarjetas. |
| `resumen` | * | Descripción corta para la home. |
| `contenido` | * | Desarrollo completo para la ficha. |
| `imagen` |  | Imagen horizontal opcional para tarjeta y ficha. |
| `color` | * | Color de marca de respaldo: azul, verde, amarillo o rojo. |
| `fecha_publicacion` | * | Momento desde el que puede publicarse. |
| `destacada` | * | Prioriza la novedad en la home. |
| `activa` | * | Permite publicar u ocultar la novedad. |

## Orden y publicación

Las novedades públicas se ordenan primero por `destacada` y luego por fecha de publicación descendente. Una novedad futura o inactiva no aparece en la home y su ficha pública responde como no encontrada.
