---
type: "Arquitectura"
title: "Despliegue en Vercel"
description: "Seguridad, ramas desplegables y operación de la base productiva."
tags: [mvp, arquitectura, despliegue, seguridad]
timestamp: 2026-07-27T00:00:00-03:00
---

# Despliegue en Vercel

Uni2 se ejecuta en Vercel con `config.settings.production` y PostgreSQL. El
proyecto mantiene separadas la atención HTTP y las tareas operativas para que
el inicio de una función serverless nunca modifique la base de datos.

### Responsabilidades

- Vercel detecta el proyecto Django mediante `manage.py`, encuentra la
  aplicación WSGI y empaqueta la función sin un entrypoint `api/index.py`.
- `vercel.json` declara explícitamente el preset `django` para que la
  configuración versionada reemplace cualquier preset `Other` heredado en el
  proyecto remoto.
- `manage.py` selecciona `config.settings.production` cuando Vercel expone
  `VERCEL=1`; fuera de Vercel conserva los settings locales. Un valor vacío de
  `DJANGO_SETTINGS_MODULE` no impide esta selección segura.
- El build usa Python 3.12, `pyproject.toml` y `uv.lock`; no mantiene una
  segunda lista de dependencias en archivos `requirements*.txt`.
- El soporte Django de Vercel detecta y publica los archivos estáticos en su
  CDN. WhiteNoise conserva el manifiesto y el servicio de respaldo dentro de
  Django. `staticfiles/` es un artefacto y no se versiona.
- Las migraciones se revisan y ejecutan como un paso explícito de operación.
- `carga_inicial` contiene únicamente datos ficticios de desarrollo y está
  bloqueado en producción mediante `ALLOW_DEMO_DATA=False`.
- Los datos reales se administran mediante los flujos de gestión y soporte
  documentados, no mediante el arranque del servidor.

### Seguridad de settings

- `DEBUG` permanece siempre en `False` dentro de
  `config.settings.production`; una variable externa no puede activarlo.
- Los dominios propios se declaran en `ALLOWED_HOSTS` sin protocolo.
- Los orígenes que pueden enviar formularios se declaran en
  `CSRF_TRUSTED_ORIGINS` con `https://`.
- Vercel expone `VERCEL_URL`, `VERCEL_BRANCH_URL` y
  `VERCEL_PROJECT_PRODUCTION_URL`. Los valores presentes se agregan como hosts
  y orígenes exactos para admitir las URLs generadas sin usar el comodín
  `.vercel.app`.
- Producción redirige a HTTPS, limita las cookies de sesión y CSRF a conexiones
  seguras y envía HSTS con una duración inicial de una hora. La duración puede
  aumentarse después de validar de forma sostenida el dominio productivo.
- `SECRET_KEY`, `DATABASE_URL` y credenciales de storage viven solamente como
  variables cifradas del entorno Production y no se versionan. `SECRET_KEY`
  debe ser largo y aleatorio; rotarlo invalida las sesiones existentes.

### Ramas y entornos

`vercel.json` mantiene solamente las decisiones propias del proyecto: región y
ramas desplegables. Habilita deploy automático para `main` y lo deshabilita
para el resto de los branches. Los previews permanecen apagados mientras no
exista una base PostgreSQL de Preview separada, con credenciales y datos
ficticios.

Nunca se configura un Preview con `DATABASE_URL`, `SECRET_KEY` o credenciales
de storage pertenecientes a Production.

### Migraciones

Un PR con cambios de esquema debe incluir su migración y mantener
compatibilidad temporal con la versión productiva anterior.

1. Revisar y aprobar el código y la migración.
2. Consultar `migrate --plan` usando las variables Production de Vercel.
3. Confirmar un respaldo cuando el cambio tenga riesgo sobre datos.
4. Aplicar la migración antes de fusionar el PR.
5. Fusionar en `main` para iniciar el deploy automático.
6. Verificar el sitio y los logs productivos.

Los cambios destructivos se dividen en entregas compatibles. Un rollback de
código no revierte automáticamente una migración.

Los comandos concretos se mantienen en el [README](../../README.md).
