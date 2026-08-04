---
type: "Arquitectura"
title: "Entorno de staging"
description: "Separación, protección, despliegue y promoción del entorno previo a Producción."
tags: [mvp, arquitectura, staging, despliegue, seguridad]
timestamp: 2026-08-02T00:00:00-03:00
---

# Entorno de staging

Staging es el entorno estable donde se valida una versión antes de publicarla.
Usa un proyecto Vercel, una base PostgreSQL, un secreto Django y un origen HTTPS
distintos de Producción.

### Circuito de ramas

```text
feature/* -> PR a staging -> deploy y aceptación en staging
staging   -> PR a main    -> deploy en Producción
```

- Todo PR ejecuta la suite completa con SQLite y el endurecimiento focalizado
  sobre un PostgreSQL efímero.
- Un push aprobado a `staging` dispara el workflow `Deploy staging`.
- El workflow despliega primero sin mover el dominio estable.
- La URL técnica debe rechazar el acceso anónimo a las vistas de negocio y
  aprobar readiness con credenciales. Manifest, iconos, service worker y
  pantalla offline deben responder sin la cabecera HTTP Basic que el worker no
  puede garantizar.
- Solamente después de esos controles se promueve el deployment.
- El dominio estable vuelve a probar readiness y el SHA promovido.
- Producción conserva su integración Git actual y sólo despliega `main`.
- Después de un release, `main` se vuelve a integrar en `staging`.

El proyecto Vercel de staging no se conecta al repositorio. El workflow lo
selecciona mediante un ID guardado en el Environment `staging` de GitHub. Esto
evita que el mismo `vercel.json` habilite ramas cruzadas en los dos proyectos.
Cada operación CLI declara además `--scope="$VERCEL_ORG_ID"`: un token puede
tener un contexto personal predeterminado y no se permite que deploy, smoke o
promoción resuelvan equipos diferentes.

### Datos

La base de staging puede partir de una copia puntual de Producción autorizada
por la responsable del proyecto. La copia conserva datos de negocio y datos
personales para que las pruebas sean representativas, por lo que se trata con
el mismo nivel de sensibilidad que Producción.

Antes de habilitarla:

- se borran todas las sesiones;
- se desactivan los usuarios copiados;
- sus contraseñas se reemplazan por valores inutilizables;
- se quitan privilegios `staff` y `superuser`;
- se regeneran todos los tokens de credencial;
- se crean un admin QA, dos asociados ficticios y un comercio ficticio con
  cuentas exclusivas;
- se cambia el epoch de datos privados de la PWA;
- se escribe como último paso transaccional un marcador persistente con ese
  epoch;
- se mantienen bloqueados correo transaccional, correo por lote y push.

Las pruebas con la copia real se limitan a las cuentas QA y a los casos
acordados. No se descargan listados, no se hacen capturas con datos personales
y no se usan datos de staging como material de clase o demostración. Las
pruebas que necesiten compartir evidencia se repiten con datos ficticios
locales. La privacidad entre usuarios y la validación de credenciales se
prueban con las entidades sintéticas creadas por el endurecimiento, no
vinculando cuentas a asociados o comercios productivos.

El bucket productivo no se comparte. Una copia de base puede conservar nombres
de archivos, pero por defecto staging muestra esos archivos como no
disponibles. Si se habilita media remota, usa un bucket privado y exclusivo,
con URLs firmadas breves y sin dominio público.

### Barreras de seguridad

`config.settings.staging` exige:

- Vercel Authentication delante de todos los deployments `.vercel.app`; sólo
  GitHub Actions obtiene un bypass temporal mediante `vercel curl` y el token
  dedicado del proyecto;
- `DEBUG=False`;
- `UNI2_ENVIRONMENT=staging`;
- PostgreSQL obligatorio;
- huellas diferentes para la base y el rol PostgreSQL de Producción y staging;
- credenciales HTTP exclusivas delante de todas las vistas de negocio, con una
  contraseña de al menos veinte caracteres que no reutiliza `SECRET_KEY`;
- `X-Robots-Tag: noindex, nofollow, noarchive`;
- `Cache-Control: private, no-store` y `Vary: Authorization` en todas las
  respuestas de staging;
- un marcador de endurecimiento que coincide con
  `UNI2_PRIVATE_DATA_EPOCH`; si falta, la aplicación responde `503`;
- cookies y redirección HTTPS heredadas del perfil productivo;
- backend de correo dummy;
- canales de correo por lote y web push deshabilitados.

Vercel Authentication, la barrera HTTP y el login de Uni2 son capas
independientes: la primera limita el proyecto al equipo, la segunda protege
Django con un secreto exclusivo y, finalmente, Uni2 aplica usuarios, grupos y
permisos.

El navegador descarga el service worker en un contexto que no garantiza el
envío de la cabecera `Authorization` usada para abrir la página. Para que
staging pueda probar instalación y offline de verdad, la barrera HTTP deja
pasar sin esas credenciales únicamente recursos neutros:

- manifest y service worker;
- páginas offline sin sesión ni datos;
- archivos estáticos versionados.

La excepción admite sólo `GET` y `HEAD`. No incluye `/media/`, readiness,
vistas públicas de negocio, login ni pantallas autenticadas. Todos esos
recursos siguen detrás de la barrera. Vercel Authentication continúa delante
del proyecto completo y las respuestas exceptuadas conservan `noindex` y
`no-store`.

Staging se identifica mediante nombre PWA, color, título, badge, banner
persistente e iconos propios con la insignia `STG`. El origen HTTPS distinto
mantiene separadas las instalaciones, cachés e IndexedDB de staging y
Producción.

### Variables del proyecto Vercel

En el ambiente Production del proyecto `uni2-staging` —“Production” es el
nombre técnico del target estable de ese proyecto— se definen:

- `DJANGO_SETTINGS_MODULE=config.settings.staging`
- `UNI2_ENVIRONMENT=staging`
- `SECRET_KEY`
- `DATABASE_URL`
- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`
- `UNI2_STAGING_ACCESS_USERNAME`
- `UNI2_STAGING_ACCESS_PASSWORD`
- `UNI2_STAGING_DATABASE_LABEL`
- `UNI2_STAGING_DATABASE_FINGERPRINT`
- `UNI2_PRODUCTION_DATABASE_FINGERPRINT`
- `UNI2_STAGING_DATABASE_ROLE_FINGERPRINT`
- `UNI2_PRODUCTION_DATABASE_ROLE_FINGERPRINT`
- `UNI2_PRIVATE_DATA_EPOCH`

El storage remoto es opcional. Si se usa, sólo admite variables con prefijo
`UNI2_STAGING_AWS_*` y las huellas
`UNI2_STAGING_STORAGE_FINGERPRINT` y
`UNI2_PRODUCTION_STORAGE_FINGERPRINT`. Las variables productivas `AWS_*` nunca
se heredan.

El Environment `staging` de GitHub contiene sólo credenciales necesarias para
desplegar y ejecutar los smoke tests:

- `VERCEL_ORG_ID`
- `VERCEL_STAGING_PROJECT_ID`
- `VERCEL_STAGING_TOKEN`
- `STAGING_ACCESS_USERNAME`
- `STAGING_ACCESS_PASSWORD`

Además define la variable no secreta
`STAGING_BASE_URL=https://uni2-staging.vercel.app`.

Los secretos de base, Django y storage no se copian a GitHub.
Tampoco se conserva un bypass estático adicional: Vercel CLI obtiene el bypass
de protección durante cada smoke test usando `VERCEL_STAGING_TOKEN`.

### Migraciones y rollback

Las migraciones siguen siendo una operación explícita. Se revisan y aplican a
la base staging desconectada antes de ejecutar el endurecimiento. El marcador
se escribe al final, cuando esquema, sesiones, usuarios y tokens ya quedaron
listos. Si el deployment nuevo falla su smoke test, el dominio conserva la
versión anterior.

Para un rollback se vuelve a promover el último deployment aprobado. Si hubo
una migración, el código anterior sólo puede restaurarse cuando esa migración
sea compatible. Un refresco de datos conserva la base staging anterior
desconectada durante una ventana breve y permite volver a ella sin tocar
Producción.
