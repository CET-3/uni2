# Cómo colaborar

Uni2 se mantiene mediante pull requests (PRs). No se trabaja directamente
sobre `main`.

## Flujo de trabajo

1. Actualizar `staging` y crear una rama con un nombre descriptivo:

   ```bash
   git switch staging
   git pull --ff-only
   git switch -c describe-el-cambio
   ```

2. Implementar el cambio y actualizar el archivo más específico de
   `especificacion/` cuando cambie arquitectura, comportamiento o navegación.
3. Ejecutar la suite local con SQLite:

   ```bash
   DB_ENGINE=sqlite uv run pytest
   ```

4. Revisar los archivos que se van a incluir y crear un commit breve en
   castellano.
5. Publicar la rama y abrir un PR contra `staging`.
6. Fusionar solamente cuando el check `pytest (SQLite)` esté aprobado y todas
   las conversaciones estén resueltas. Los cambios del circuito staging
   también deben aprobar `Endurecimiento staging (PostgreSQL)`.

El merge en `staging` despliega el entorno HTTPS de prueba. Después de la
aceptación se abre un PR de release `staging -> main`. Producción se despliega
solamente al fusionar ese PR. Al terminar, `main` se vuelve a integrar en
`staging`.

`main` y `staging` no admiten pushes directos, force-push ni borrado. Las ramas
de trabajo no generan previews ni reciben acceso a bases remotas.

Un hotfix parte de `main`, se valida primero en staging siempre que la urgencia
lo permita y, después del deploy productivo, se integra de vuelta para evitar
que el siguiente release lo pierda.

## Datos que nunca se versionan

No incluir archivos `.env`, bases SQLite, datos reales, credenciales ni
exports operativos. Los archivos `.env.example` y `.env.postgres.example`
contienen solamente nombres de variables y valores ficticios.

Si un secreto entra por error en un commit, no alcanza con borrarlo en otro
commit: hay que avisar, rotarlo y limpiar el historial antes de publicar.

El historial de `main` se reescribió el 28 de julio de 2026 para retirar
archivos de entorno antiguos. Un clon creado antes de esa fecha debe
reclonarse; no se deben fusionar ramas basadas en el historial anterior.
