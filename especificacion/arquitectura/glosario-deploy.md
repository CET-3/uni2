---
type: "Arquitectura"
title: "Glosario de deploy y releases"
description: "Conceptos básicos para entender la configuración, protección y promoción de versiones de Uni2."
tags: [mvp, arquitectura, deploy, releases, aprendizaje]
timestamp: 2026-08-04T00:00:00-03:00
---

# Glosario de deploy y releases

Este documento explica los términos que aparecen en el deploy de Uni2 y el
circuito que sigue una versión desde una rama de trabajo hasta Production.

## Ambientes y ramas

El código se mueve por ramas y cada ambiente tiene su propia configuración:

```text
feature/* -> PR hacia staging -> deploy y aceptación en staging
staging   -> PR hacia main    -> deploy en Production
```

Un `push` a una rama de feature actualiza el PR, pero no despliega staging. El
deploy de staging ocurre cuando el cambio llega a la rama permanente `staging`.
Production se despliega desde `main`.

## Circuito de un release

1. Se implementa un cambio en una rama `feature/*`.
2. Se abre un PR hacia `staging`.
3. CI ejecuta la suite de tests y las validaciones de endurecimiento.
4. Al llegar el cambio a `staging`, GitHub Actions descarga ese commit exacto.
5. El workflow crea un deployment técnico en el proyecto Vercel de staging.
6. Se prueban seguridad, readiness, base de datos, manifest, iconos, service
   worker y pantalla offline.
7. Si todas las pruebas pasan, se promueve el deployment al dominio estable de
   staging.
8. El equipo valida la versión en staging.
9. Se abre un PR desde `staging` hacia `main`.
10. Al fusionarlo, Vercel despliega Production.

Si falla una validación antes de la promoción, el dominio estable conserva la
versión anterior. Un rollback consiste en volver a promover el último
deployment aprobado, siempre que las migraciones de base sean compatibles.

## Variables de entorno

Una variable de entorno es un valor que el programa recibe desde afuera del
código. Permite usar el mismo código en ambientes diferentes:

```text
código igual + variables de staging    = staging
código igual + variables de Production = Production
```

Ejemplos:

- `UNI2_ENVIRONMENT=staging` indica el ambiente.
- `DATABASE_URL` indica a qué base conectarse.
- `STAGING_BASE_URL` indica el dominio estable de staging.
- `DEBUG` controla una opción de ejecución, aunque en Production Uni2 lo
  deshabilita por código.

Una variable no es necesariamente secreta. Su clasificación depende de su
contenido y del riesgo de exponerla.

## Secreto

Un secreto es un valor confidencial que permite acceder, autenticarse o
descifrar algo. Ejemplos:

- `SECRET_KEY` de Django;
- `DATABASE_URL` con contraseña;
- contraseñas de acceso HTTP a staging;
- claves AWS;
- tokens de Vercel.

Los secretos se guardan en GitHub Secrets, Vercel Environment Variables o
archivos locales ignorados por Git. Nunca se escriben en el repositorio, en
argumentos documentados ni en logs.

## Token

Un token es una credencial técnica para usar una API o herramienta. Por
ejemplo, `VERCEL_STAGING_TOKEN` permite que GitHub Actions use Vercel para
desplegar, probar y promover un deployment.

No representa necesariamente a una persona y no debe confundirse con la
contraseña de un usuario de Uni2. Como todo token permite realizar acciones,
debe tener el menor alcance posible y almacenarse como secreto.

## Scope

El `scope` indica dentro de qué organización o equipo debe operar Vercel.

El workflow declara explícitamente:

```bash
--scope="$VERCEL_ORG_ID"
```

Esto evita que un token con acceso a varios equipos use por accidente otro
proyecto u organización.

## Bypass

Un bypass es una excepción controlada a una protección.

Staging tiene varias barreras independientes:

1. Vercel Authentication limita el acceso al proyecto.
2. La barrera HTTP de Django protege las vistas del sitio.
3. El login de Uni2 aplica usuarios, grupos y permisos.

GitHub Actions necesita probar un deployment protegido. Para eso Vercel CLI
obtiene un bypass temporal mediante el token del proyecto durante los smoke
tests. Esto no vuelve público a staging ni elimina las protecciones para las
personas usuarias.

La barrera HTTP también permite sin credenciales algunos recursos neutros que
la PWA necesita descargar, como el manifest, el service worker, las páginas
offline y los archivos estáticos. No permite de esa forma readiness, login,
media ni pantallas autenticadas.

## Endurecimiento

El endurecimiento es el conjunto de acciones que convierte una copia de datos
o un ambiente potencialmente peligroso en un ambiente seguro para pruebas.

Cuando staging parte de una copia de Production, el comando
`preparar_copia_staging`:

- elimina sesiones;
- conserva usuarios, contraseñas, permisos, privilegios, perfiles y tokens;
- escribe el marcador final de staging.

Hasta que el proceso termina correctamente, staging no se considera listo y
puede responder `503`. Las credenciales copiadas siguen siendo válidas en
staging, por lo que la barrera HTTP y el aislamiento de la base son obligatorios.
La configuración del entorno mantiene deshabilitados el correo transaccional,
el correo por lote y push durante el refresco.

El endurecimiento reduce riesgos, pero staging sigue conteniendo datos y
credenciales sensibles si se creó desde Production. Por eso se hacen pruebas
controladas, no se descargan listados y no se reutilizan datos reales como
material de demostración.

## Huella o fingerprint

Una huella, o `fingerprint`, es una identificación calculada de una
configuración. En Uni2 se usa para verificar bases de datos, roles de
PostgreSQL y storage.

La huella no contiene la contraseña ni permite conectarse. Sirve para comparar:

```text
huella declarada = huella del recurso realmente conectado
```

Staging también comprueba que sus huellas sean diferentes de las de
Production. Así se puede detectar una configuración equivocada, como una
aplicación de staging conectada a la base productiva.

Para storage, la huella identifica bucket, endpoint y dominio personalizado,
pero nunca incluye las claves de acceso.

## Promoción

Promover es convertir un deployment ya probado en la versión estable visible
por el dominio del ambiente.

El workflow de staging no mueve el dominio estable inmediatamente. Primero:

1. crea un deployment técnico;
2. ejecuta los smoke tests sobre esa URL técnica;
3. verifica que el commit y la configuración sean los esperados;
4. ejecuta `vercel promote`;
5. vuelve a probar el dominio estable.

Esto separa “el código fue construido” de “la versión fue aceptada y publicada
como estable”.

## Regla mental

Para analizar un deploy, conviene preguntar:

- ¿Qué commit exacto se está desplegando?
- ¿En qué ambiente y proyecto se está desplegando?
- ¿Qué variables de entorno recibe?
- ¿Qué secretos necesita y dónde están guardados?
- ¿Qué barreras protegen el ambiente?
- ¿Qué huellas confirman que apunta a los recursos correctos?
- ¿Qué pruebas deben pasar antes de promover?
- ¿Cómo se vuelve a la versión anterior si algo falla?
