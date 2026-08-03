---
type: "Entidad"
title: "EstadoDatosStaging"
description: "Marcador técnico que habilita una copia endurecida en el entorno de staging."
tags: [mvp, entidad, staging, seguridad]
timestamp: 2026-08-02T00:00:00-03:00
---

# EstadoDatosStaging

Registro técnico único que demuestra que el endurecimiento de una copia de
Producción terminó correctamente. No contiene datos personales y no se
administra desde una pantalla ni desde el admin de Django.

| Campo | Tipo | Descripción |
|---|---|---|
| `clave`* | texto breve | Clave primaria fija `actual`; mantiene un único estado vigente. |
| `refresh_id`* | texto breve | Identificador del refresco; debe coincidir con `UNI2_PRIVATE_DATA_EPOCH`. |
| `listo_desde`* | fecha y hora | Momento en que terminó la transacción de endurecimiento. |

El comando `preparar_copia_staging` actualiza este registro como último paso de
la misma transacción que elimina sesiones, invalida usuarios y regenera tokens.
El middleware de staging no sirve la aplicación si el registro falta o si su
`refresh_id` no coincide con el epoch publicado.
