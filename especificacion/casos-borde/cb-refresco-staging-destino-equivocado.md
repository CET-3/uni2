---
type: "Caso borde"
title: "CB-refresco-staging-destino-equivocado"
description: "La operación de copia o endurecimiento apunta a una base distinta de la declarada."
tags: [mvp, staging, seguridad]
timestamp: 2026-08-02T00:00:00-03:00
---

# CB-refresco-staging-destino-equivocado

### Situación

La URL o el rol configurado coincide con Producción, una huella no coincide con
la declarada o la confirmación escrita no coincide con el nombre de staging.

### Respuesta esperada

- Los settings o el comando abortan antes de modificar datos.
- No se usan opciones destructivas como `--clean` o `--create`.
- Se revisan host, base, rol y huellas fuera de los logs públicos.
- La operación sólo se reinicia sobre una base staging nueva.
