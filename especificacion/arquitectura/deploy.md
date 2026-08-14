---
type: "Arquitectura"
title: "Configuración de deploy"
description: "Inventario de variables de entorno, secretos y valores automáticos usados por Production, staging y GitHub Actions."
tags: [mvp, arquitectura, deploy, seguridad, releases]
timestamp: 2026-08-04T00:00:00-03:00
---

# Configuración de deploy

Este documento registra qué variables necesita cada ambiente y dónde se
configuran. No contiene valores reales: sólo nombres, propósito y clasificación.

## Cómo leer las tablas

- **No secreto:** puede documentarse y revisarse sin ocultarlo.
- **Sensible:** no es una contraseña, pero conviene limitar su exposición.
- **Secreto:** debe guardarse en un almacén de secretos y nunca en el código.
- **Obligatoria:** el ambiente no debe iniciar correctamente sin ella.
- **Opcional:** sólo se necesita cuando se habilita una funcionalidad.

Guardar una variable como GitHub Secret no siempre significa que su valor sea
secreto por naturaleza. Por ejemplo, un identificador de proyecto puede
protegerse como secret para centralizar la configuración, aunque no permita
autenticarse por sí solo.

## Vercel — Production

Estas variables pertenecen al proyecto Vercel productivo.

| Variable | Clasificación | Estado | Propósito |
| --- | --- | --- | --- |
| `SECRET_KEY` | Secreto | Obligatoria | Firma y seguridad de Django. |
| `DATABASE_URL` | Secreto | Obligatoria | Conexión a la base productiva. |
| `ALLOWED_HOSTS` | No secreto | Obligatoria | Hosts permitidos por Django. |
| `CSRF_TRUSTED_ORIGINS` | No secreto | Obligatoria | Orígenes HTTPS confiables. |
| `AWS_STORAGE_BUCKET_NAME` | No secreto | Opcional | Bucket productivo para archivos subidos. |
| `AWS_ACCESS_KEY_ID` | Sensible | Opcional | Identificador de acceso al storage. |
| `AWS_SECRET_ACCESS_KEY` | Secreto | Opcional | Clave secreta del storage. |
| `AWS_S3_ENDPOINT_URL` | No secreto | Opcional | Endpoint S3-compatible. |
| `AWS_S3_REGION_NAME` | No secreto | Opcional | Región del storage. |
| `AWS_S3_CUSTOM_DOMAIN` | No secreto | Opcional | Dominio público opcional del storage. |

Los valores vigentes para los hosts públicos y técnicos admitidos son:

```text
ALLOWED_HOSTS=uni2.app,www.uni2.app,uni2-ashy.vercel.app
CSRF_TRUSTED_ORIGINS=https://uni2.app,https://www.uni2.app,https://uni2-ashy.vercel.app
```

Estos valores pertenecen únicamente al entorno Production. Cambiarlos exige
crear un nuevo deployment para que el runtime reciba las variables actualizadas.

Vercel agrega automáticamente variables como `VERCEL_URL`,
`VERCEL_BRANCH_URL` y `VERCEL_PROJECT_PRODUCTION_URL`. No se copian ni se
versionan manualmente.

## Vercel — staging

Estas variables pertenecen al proyecto separado `uni2-staging`. En Vercel, el
target estable de este proyecto se llama técnicamente `Production`; eso no lo
convierte en el ambiente productivo de Uni2.

| Variable | Clasificación | Estado | Propósito |
| --- | --- | --- | --- |
| `DJANGO_SETTINGS_MODULE` | No secreto | Obligatoria | Selecciona `config.settings.staging`. |
| `UNI2_ENVIRONMENT` | No secreto | Obligatoria | Confirma que el ambiente es staging. |
| `SECRET_KEY` | Secreto | Obligatoria | Clave Django exclusiva de staging. |
| `DATABASE_URL` | Secreto | Obligatoria | Conexión a la base staging. |
| `ALLOWED_HOSTS` | No secreto | Obligatoria | Hosts permitidos. |
| `CSRF_TRUSTED_ORIGINS` | No secreto | Obligatoria | Orígenes HTTPS confiables. |
| `UNI2_STAGING_ACCESS_USERNAME` | Sensible | Obligatoria | Usuario de la barrera HTTP. |
| `UNI2_STAGING_ACCESS_PASSWORD` | Secreto | Obligatoria | Contraseña de la barrera HTTP. |
| `UNI2_STAGING_DATABASE_LABEL` | No secreto | Obligatoria | Nombre esperado de la base staging. |
| `UNI2_STAGING_DATABASE_FINGERPRINT` | No secreto | Obligatoria | Huella de la base staging. |
| `UNI2_PRODUCTION_DATABASE_FINGERPRINT` | No secreto | Obligatoria | Huella de comparación de Production. |
| `UNI2_STAGING_DATABASE_ROLE_FINGERPRINT` | No secreto | Obligatoria | Huella del rol PostgreSQL staging. |
| `UNI2_PRODUCTION_DATABASE_ROLE_FINGERPRINT` | No secreto | Obligatoria | Huella del rol PostgreSQL productivo. |
| `UNI2_PRIVATE_DATA_EPOCH` | Sensible | Obligatoria | Identificador del refresco de datos privados. |

### Storage staging opcional

Staging no hereda las variables `AWS_*` de Production. Si se habilita un bucket
privado exclusivo, se usan solamente estas variables:

| Variable | Clasificación | Estado | Propósito |
| --- | --- | --- | --- |
| `UNI2_STAGING_AWS_STORAGE_BUCKET_NAME` | No secreto | Opcional | Bucket privado de staging. |
| `UNI2_STAGING_AWS_ACCESS_KEY_ID` | Sensible | Condicional | Identificador de acceso al bucket. |
| `UNI2_STAGING_AWS_SECRET_ACCESS_KEY` | Secreto | Condicional | Clave de acceso al bucket. |
| `UNI2_STAGING_AWS_S3_ENDPOINT_URL` | No secreto | Opcional | Endpoint S3-compatible. |
| `UNI2_STAGING_AWS_S3_REGION_NAME` | No secreto | Opcional | Región del bucket. |
| `UNI2_STAGING_STORAGE_FINGERPRINT` | No secreto | Condicional | Huella del bucket staging. |
| `UNI2_PRODUCTION_STORAGE_FINGERPRINT` | No secreto | Condicional | Huella de comparación de Production. |

Cuando se define el bucket, las variables marcadas como condicionales pasan a
ser obligatorias. Las huellas deben ser diferentes de las productivas.

## GitHub Actions — Environment `staging`

Estas variables se configuran en el Environment `staging` de GitHub, no en el
repositorio como texto plano.

| Nombre | Tipo recomendado en GitHub | Clasificación | Propósito |
| --- | --- | --- | --- |
| `STAGING_BASE_URL` | Variable | No secreto | Dominio estable que se verifica después de promover. |
| `VERCEL_ORG_ID` | Secret | Sensible | Organización o equipo usado como `scope`. |
| `VERCEL_STAGING_PROJECT_ID` | Secret | Sensible | Proyecto Vercel de staging. |
| `VERCEL_STAGING_TOKEN` | Secret | Secreto | Permite desplegar, probar y promover en Vercel. |
| `STAGING_ACCESS_USERNAME` | Secret | Sensible | Usuario para los smoke tests protegidos. |
| `STAGING_ACCESS_PASSWORD` | Secret | Secreto | Contraseña para los smoke tests protegidos. |

El workflow construye además valores temporales, como `PWA_BUILD_ID` a partir
de `github.sha` y `DEPLOYMENT_URL` a partir de la URL devuelta por Vercel. No se
cargan manualmente.

## Reglas de almacenamiento

- Los valores secretos no se guardan en el repositorio, commits, issues ni
  documentación.
- Las contraseñas no se pasan como argumentos de comandos ni se escriben en
  archivos versionados.
- Production y staging tienen secretos y bases diferentes.
- No se copian automáticamente secretos de Production a staging.
- Las huellas no reemplazan a las credenciales: sólo verifican identidad y
  separación de recursos.
- Ante una duda, se trata un valor como secreto hasta confirmar que no habilita
  acceso ni revela información sensible.

## Referencias

- [Entorno de staging](staging.md)
- [Refresco de datos de staging](refresco-staging.md)
- [Glosario de deploy y releases](glosario-deploy.md)
