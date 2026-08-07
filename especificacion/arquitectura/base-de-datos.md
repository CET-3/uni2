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
| Staging | PostgreSQL | Usar `config.settings.staging` sobre una copia productiva endurecida |
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
- Cambiar de motor no migra datos existentes. Cada base local se inicializa
  aplicando migraciones y puede recibir los datos ficticios de `carga_inicial`.
- `carga_inicial` sólo está habilitado en desarrollo local y tests. Producción
  recibe migraciones mediante el procedimiento operativo documentado y sus
  datos se administran por los flujos previstos; nunca carga usuarios con
  contraseñas de demostración.
- Staging puede recibir una copia puntual de Producción, pero sólo sobre una
  base independiente. Antes de conectarla se eliminan sesiones, se invalidan
  accesos productivos y se regeneran tokens según el
  [procedimiento de refresco](refresco-staging.md).

Los comandos de instalación y puesta en marcha se mantienen en el
[README del proyecto](../../README.md). Para quienes recién empiezan, hay una
[guía de inicio para Windows con Python, uv y Django](../guia-windows-python-django.md).
