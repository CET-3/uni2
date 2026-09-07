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
para el resto de los branches. Los previews de cada PR permanecen apagados.

Staging usa un segundo proyecto Vercel llamado `uni2-staging`, sin integración
Git. Un push a la rama permanente `staging` ejecuta primero la suite y, sólo si
aprueba, un workflow selecciona ese proyecto por ID. Despliega sin mover el
dominio estable, prueba autorización, readiness, manifest, iconos, service
worker y pantalla offline, y después lo promueve. Finalmente vuelve a probar
readiness sobre el dominio estable. Esto evita conectar el clon productivo a
ramas arbitrarias.

GitHub Actions ejecuta `pytest` con Python 3.12 y las dependencias fijadas en
`uv.lock`. Cada PR y cada actualización de `main` corren la suite completa con
SQLite y el endurecimiento focalizado contra un PostgreSQL 16 efímero. Un push
a `staging` reutiliza ese workflow antes del deploy. Ningún job recibe secretos
ni credenciales de bases remotas.

El repositorio es público para que los estudiantes puedan clonarlo sin
pertenecer a la organización. Todo cambio se entrega mediante un PR. La rama
`main` exige el check `pytest (SQLite)` actualizado, aplica la protección
también a administradores y no admite force-push ni borrado. No se exige una
segunda aprobación mientras el proyecto tenga una única mantenedora.

El dominio público canónico de Production es `https://www.uni2.app/`.
`https://uni2.app/` redirige hacia el dominio canónico y
`https://uni2-ashy.vercel.app/` permanece admitido como dirección técnica
secundaria; no se comunica como acceso público principal.

Porkbun conserva los nameservers autoritativos y administra el DNS. El dominio
raíz usa el registro `A` indicado por Vercel y `www` usa el `CNAME` específico
asignado al proyecto. Vercel termina HTTPS, publica la aplicación y aplica la
redirección del dominio raíz. Las URLs técnicas de deployments y previews
permanecen detrás de Standard Protection de Vercel.

Nunca se configura un Preview con `DATABASE_URL`, `SECRET_KEY` o credenciales
de storage pertenecientes a Production.

### Staging HTTPS para la PWA

Las pruebas automáticas del service worker pueden usar `localhost`, que los
navegadores tratan como contexto seguro. Una IP de red local servida por HTTP
no es un contexto seguro y no permite validar la instalación desde un
teléfono.

Las pruebas físicas se realizan en un entorno staging separado con:

- URL HTTPS estable;
- Vercel Authentication sobre todos los deployments técnicos;
- PostgreSQL propio que puede recibir una copia productiva endurecida;
- `SECRET_KEY` propio;
- bucket o prefijo de media propio;
- hosts y orígenes CSRF propios;
- barrera HTTP delante de Django y login propio de Uni2;
- ninguna credencial, sesión, contraseña ni token reutilizable de Production.

La copia mantiene datos personales, por lo que staging se protege y opera con
la misma sensibilidad que Producción. El
[refresco de datos](refresco-staging.md) borra sesiones, invalida usuarios
copiados, retira privilegios y regenera los tokens antes de conectar la base.

Una URL estable es necesaria para instalar la versión A, desplegar la B sobre
el mismo origen y probar el ciclo real de actualización. La protección de
Vercel no debe impedir que el manifest, el worker y los estáticos se soliciten
desde la sesión de prueba.

### Controles PWA del despliegue

En staging y después del deploy productivo se comprueba:

- el acceso anónimo queda detenido antes de las vistas de staging;
- todas las respuestas staging llevan `X-Robots-Tag` restrictivo;
- readiness confirma la conexión, el marcador de endurecimiento, el epoch y el
  SHA exacto desplegado. También devuelve `pending_migrations`: si no está
  vacío responde 503 e informa `reason: migrations_pending`, para que el
  diagnóstico indique la migración concreta que falta;
- `/manifest.webmanifest` responde 200 como
  `application/manifest+json`;
- todos los iconos del manifest responden 200 y tienen el tamaño declarado;
- staging usa exclusivamente los iconos naranjas con insignia `STG`;
- `/service-worker.js` responde 200 como JavaScript, con
  `Service-Worker-Allowed: /` y política de no caché;
- el worker controla el scope `/` y usa el ID del commit desplegado;
- si readiness responde 503, el smoke test conserva y muestra su JSON para
  distinguir migraciones pendientes de otros errores de disponibilidad;
- `/sin-conexion/` abre sin datos de usuario;
- una respuesta pública anónima lleva
  `X-Uni2-PWA-Cacheable: public` y `Vary: Cookie`;
- una respuesta autenticada lleva `Cache-Control: private, no-store`;
- los estáticos no dependen de un CDN externo;
- no existe una migración inesperada.

Staging muestra un banner persistente, un nombre PWA propio y un color
distintivo. `UNI2_PRIVATE_DATA_EPOCH` cambia con cada refresco para que una PWA
instalada elimine cualquier credencial offline ligada a la copia anterior al
volver a conectarse. Durante el offline absoluto no existe revocación remota;
continúa aplicando el vencimiento local máximo de siete días.

La prueba manual completa está en
[Progressive Web App](../pruebas-manuales/pwa.md). Chromium automatizado no
reemplaza Android e iOS reales.

### Gate de release PWA

La PWA sólo puede pasar a Production cuando:

1. pytest completo está aprobado;
2. `collectstatic` contiene los recursos PWA y vendor;
3. staging supera privacidad entre dos usuarios y expiración de siete días;
4. un POST offline no se reenvía al recuperar conexión;
5. la actualización no recarga un formulario;
6. Android e iOS reales superan la matriz mínima;
7. se ensayó el rollback en staging;
8. especificación y README coinciden con el build.

### Migraciones

Un PR con cambios de esquema debe incluir su migración y mantener
compatibilidad temporal con la versión productiva anterior.

1. Revisar y aprobar el código y la migración.
2. Ejecutar `scripts/preflight-production-deploy.sh` desde un workspace con
   `.env.production` y revisar el plan.
3. Confirmar un respaldo cuando el cambio tenga riesgo sobre datos.
4. Aplicar la migración antes de fusionar el PR.
5. Fusionar en `main` para iniciar el deploy automático.
6. Verificar el sitio y los logs productivos.

Los cambios destructivos se dividen en entregas compatibles. Un rollback de
código no revierte automáticamente una migración.

En staging se aplica el mismo criterio antes de actualizar la rama estable:
primero se revisa y aplica la migración compatible sobre la base staging y
después se permite el deploy. El workflow no conoce `DATABASE_URL` y no ejecuta
migraciones durante el build.

El procedimiento productivo es determinista y no usa `vercel env run` para
obtener credenciales: esa operación puede devolver variables vacías. Antes de
fusionar un PR con cambios de esquema, se ejecutan exactamente estos pasos
desde un workspace que tenga `.env.production` con `DATABASE_URL`:

```bash
scripts/preflight-production-deploy.sh
scripts/preflight-production-deploy.sh --apply
```

El plan se revisa y la migración se aplica antes de fusionar `staging` en
`main`. Si cualquiera de los dos comandos falla, no se fusiona ni se prueba el
deploy. Vercel sólo publica el código; nunca se toma como ejecutor de
migraciones.

Los comandos concretos se mantienen en el [README](../../README.md).

### Rollback de la PWA

Revertir código o retirar `/service-worker.js` no desinstala workers ya
registrados. Nunca se responde simplemente 404 en esa URL como estrategia de
rollback.

El rollback operativo publica primero, en la misma URL y alcance, un worker de
limpieza que:

1. borra los cachés cuyo prefijo pertenece a Uni2;
2. borra el almacenamiento privado de credencial;
3. avisa a las ventanas abiertas;
4. se desregistra;
5. deja continuar la navegación como web normal.

El endpoint de limpieza se mantiene durante el período definido por operación
para alcanzar dispositivos que vuelven a conectarse más tarde. Sólo después
se retira el registro cliente. Ante una falla que no exige retirar la PWA, se
despliega una corrección compatible conservando la misma URL del worker.
