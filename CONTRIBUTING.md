# Cómo colaborar

Uni2 se mantiene mediante pull requests (PRs). No se trabaja directamente
sobre `main`.

## Flujo de trabajo

1. Actualizar `main` y crear una rama con un nombre descriptivo:

   ```bash
   git switch main
   git pull --ff-only
   git switch -c describe-el-cambio
   ```

2. Implementar el cambio y actualizar el archivo más específico de
   `especificacion/` cuando cambie arquitectura, comportamiento o navegación.
3. Ejecutar las pruebas con SQLite:

   ```bash
   DB_ENGINE=sqlite uv run pytest
   ```

4. Revisar los archivos que se van a incluir y crear un commit breve en
   castellano.
5. Publicar la rama y abrir un PR contra `main`.
6. Fusionar solamente cuando el check `pytest (SQLite)` esté aprobado y todas
   las conversaciones estén resueltas.

`main` no admite pushes directos, force-push ni borrado. Vercel despliega
automáticamente sólo después de fusionar un PR en `main`; las ramas de trabajo
no generan previews mientras no exista una base de datos separada para ese
entorno.

## Datos que nunca se versionan

No incluir archivos `.env`, bases SQLite, datos reales, credenciales ni
exports operativos. Los archivos `.env.example` y `.env.postgres.example`
contienen solamente nombres de variables y valores ficticios.

Si un secreto entra por error en un commit, no alcanza con borrarlo en otro
commit: hay que avisar, rotarlo y limpiar el historial antes de publicar.

El historial de `main` se reescribió el 28 de julio de 2026 para retirar
archivos de entorno antiguos. Un clon creado antes de esa fecha debe
reclonarse; no se deben fusionar ramas basadas en el historial anterior.
