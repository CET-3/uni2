# Registro de errores y ejecución del deploy a staging

Tarea: publicar los cambios de botones e idempotencia mediante el PR #53.
Este registro se mantiene durante la ejecución para revisar el procedimiento
después. No contiene secretos ni datos de negocio.

## Errores cometidos

### 1. Consultar GitHub y actualizar Git desde un sandbox sin acceso suficiente

- Comandos: `gh pr list ...` y `git fetch origin`.
- Resultado: conexión a `api.github.com` fallida y `.git/FETCH_HEAD` de sólo lectura.
- Causa: no anticipé las restricciones de red y escritura de `.git` del entorno.
- Impacto: demora y repetición de comandos; no se modificó código ni una base remota.
- Corrección comprobada: ejecutar las operaciones con la autorización de entorno correspondiente.
- Para próximos deploys: revisar las restricciones antes de empezar y mantener separadas consultas y operaciones que escriben Git.

### 2. Ejecutar Vercel CLI sin considerar que escribe en su caché

- Comando: `vercel project inspect uni2-staging --scope <equipo>`.
- Resultado: errores EROFS al escribir `vercel-latest.lock` y `vercel-latest.log` en la caché local.
- Causa: el proceso auxiliar de actualización de la CLI necesita escribir fuera del workspace; no lo contemplé.
- Impacto: salida de error y repetición de la consulta. Ningún deployment ni migración ejecutados.
- Corrección comprobada: la consulta con permisos de entorno adecuados confirmó `uni2-staging`.

### 3. Asumir que las variables de proyecto aislaban `vercel env run`

- Comando: `VERCEL_PROJECT_ID=<staging> VERCEL_ORG_ID=<equipo> vercel env run --environment production --scope <equipo> -- env DJANGO_SETTINGS_MODULE=config.settings.staging .../manage.py migrate --plan`, desde el repositorio.
- Contexto conocido: `.vercel/project.json` del repositorio apunta al proyecto productivo `uni2`.
- Resultado: la CLI informó `Loaded env from .../uni2/.env`; Django rechazó la configuración con `El perfil staging requiere UNI2_ENVIRONMENT=staging`.
- Error de criterio: confié en el override sin verificar previamente el proyecto y ambiente efectivos. No correspondía usar ese directorio para una operación administrativa de staging.
- Causa comprobada: el ambiente entregado al proceso no cumplía la identidad de staging. Queda por determinar, inspeccionando la CLI, qué precedencia tuvieron el vínculo local, las variables y `.env`; no se presenta una hipótesis como causa confirmada.
- Impacto: falló la consulta de plan antes de ejecutar migraciones; no se escribió la base mediante ese comando.
- Corrección preparada: directorio temporal separado, vinculado explícitamente con `vercel link --project uni2-staging --scope <equipo>`, sin `.env` del repositorio. Se verificó su `.vercel/project.json`.
- Para próximos deploys: usar siempre ese aislamiento y comprobar perfil e identidad antes del plan. Nunca resolver el error forzando `UNI2_ENVIRONMENT=staging` sobre variables de procedencia incierta.

### 4. Utilizar una opción de CLI deprecada

- Comando de vinculación: `vercel link --yes --team <equipo> --project uni2-staging --cwd <directorio-temporal>`.
- Resultado: la operación funcionó, pero avisó que `--team` está deprecado.
- Corrección para próximos comandos: usar `--scope`, como indica la documentación del proyecto.
- Impacto: ninguno sobre los recursos; comando innecesariamente desactualizado.

### 5. Perder la salida de una consulta al interrumpirse el turno

- Operación: seguimiento del segundo `migrate --plan`, desde el directorio aislado.
- Resultado: al retomar, el identificador de proceso ya no existía y no se recuperó su salida.
- Impacto: no se puede afirmar el resultado de esa consulta. Era sólo lectura.
- Corrección: repetir únicamente la consulta y guardar su salida. Las futuras operaciones de escritura deben registrar su resultado para poder reconciliarlo sin repetirlas a ciegas.

## Estado comprobado al iniciar este registro

- PR creado: https://github.com/CET-3/uni2/pull/53
- Commit inicial: `986c502dcbf538301a2be19ff426ce47b37d5ebc`.
- Proyecto staging confirmado y directorio temporal vinculado exclusivamente a él.
- No se ejecutó todavía un comando de aplicación de migraciones en esta tarea.
- El PR todavía no se integró; no se disparó el deploy de estos cambios.

## Continuación y resultados

Se agregan aquí los resultados comprobados, nuevos errores y comandos que
finalmente funcionen. La documentación operativa estable se mantiene en
`especificacion/arquitectura/`.

### 6. La configuración descargada siguió vacía desde el directorio aislado

- La segunda consulta guardada repitió el rechazo de `UNI2_ENVIRONMENT`.
- Diagnóstico sin secretos: `env run` entregó vacíos `UNI2_ENVIRONMENT`,
  `DJANGO_SETTINGS_MODULE` y `DATABASE_URL`. `env ls` confirmó sus nombres en
  `uni2-staging`; `env pull` también descargó esas claves vacías.
- Se comprobó que esas variables no estaban presentes en el proceso padre.
  Por eso no corresponde atribuir este segundo fallo a variables vacías
  heredadas de la shell ni dar por resuelto el problema sólo con `--cwd`.
- La causa de los valores vacíos del proveedor/CLI queda pendiente; no se
  modificaron variables remotas para intentar solucionarlo.
- Error adicional: no inspeccioné primero la existencia de `.env.staging`,
  que ya estaba disponible e ignorado por Git. Se verifica su identidad antes
  de utilizarlo como configuración administrativa local.

### 7. Las nuevas pruebas de navegador agotaron el tiempo en CI

- Workflow inicial: `34040722428`, job SQLite `101506857578`.
- Resultado: 713 pruebas aprobadas, una omitida y dos timeouts de 45 segundos
  al esperar que Chromium finalizara `--dump-dom --virtual-time-budget=10000`.
- Error de implementación: hice depender la finalización de la prueba de la
  salida del navegador; además el timeout no conservaba un diagnóstico útil
  del estado de la página.
- Corrección: la página ahora comunica explícitamente PASS/FAIL al servidor
  local; Python espera ese resultado y cierra Chromium. Se usa reloj real y
  se conserva el log y la cantidad de POST recibidos ante timeout.
- Verificación local de la corrección: ambas variantes pasan. Falta confirmar
  el nuevo commit en CI antes de integrar el PR.
- El job PostgreSQL original sí aprobó los tres casos de idempotencia,
  incluido el cobro concurrente, sin omitirlo.

### Plan de migraciones finalmente verificado

La configuración local `.env.staging` contiene los identificadores correctos
y valores no vacíos. El perfil `config.settings.staging` aceptó las huellas
de base y rol. Comando exitoso:

```bash
uv run --env-file .env.staging -- env DJANGO_SETTINGS_MODULE=config.settings.staging python manage.py migrate --plan
```

Resultado: únicamente `asociados.0011_solicitudasociacion_clave_operacion` y
`cuotas.0006_pago_clave_operacion`, ambas agregan un UUID nullable y único.
La salida se guardó en `/tmp/uni2-staging-actions-plan-local.log`.
