---
type: "Arquitectura"
title: "Base de datos por entorno"
description: "Motores de base de datos usados en aprendizaje, desarrollo y producción."
tags: [mvp, arquitectura, base-de-datos]
timestamp: 2026-07-26T00:00:00-03:00
---

# Base de datos por entorno

Uni2 admite SQLite y PostgreSQL sin cambiar el código de la aplicación. Los
dos perfiles locales usan `config.settings.local`; la variable `DB_ENGINE`
selecciona el motor.

### Perfiles

| Entorno | Motor | Configuración |
|---|---|---|
| Alumnos | SQLite | Copiar `.env.example` como `.env` |
| Desarrollo con PostgreSQL | PostgreSQL | Copiar `.env.postgres.example` como `.env` y completar las credenciales |
| Producción | PostgreSQL | Usar `config.settings.production` y definir `DATABASE_URL` |

SQLite es el perfil recomendado para alumnos porque viene incluido con Python,
no necesita un servidor y permite que cada persona trabaje con una base local
independiente en `db.sqlite3`. Este archivo es operativo y no se versiona.

PostgreSQL se mantiene para producción y para quienes necesiten verificar el
comportamiento en el mismo motor usado por el despliegue. Producción no depende
de `DB_ENGINE`: `config.settings.production` reemplaza la configuración de base
de datos y exige `DATABASE_URL`.

### Compatibilidad

- Los modelos, migraciones, selectors y services deben funcionar en SQLite y
  PostgreSQL.
- Evitar SQL manual y funciones exclusivas de un motor salvo que exista una
  necesidad documentada y pruebas específicas.
- La suite habitual usa el motor elegido en `.env`.
- Antes de integrar cambios de persistencia o consultas, se debe verificar al
  menos SQLite. Los cambios que dependan del comportamiento del motor también
  deben probarse con PostgreSQL.
- Cambiar de motor no migra datos existentes. Cada base se inicializa aplicando
  migraciones y ejecutando `carga_inicial`.

Los comandos de instalación y puesta en marcha se mantienen en el
[README del proyecto](../../README.md).
