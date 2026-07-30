---
type: "Caso de uso"
title: "CU-importar-comercios-iniciales"
description: "Actor: Administrador"
tags: [mvp, caso-de-uso]
timestamp: 2026-07-29T00:00:00-03:00
---

# CU-importar-comercios-iniciales

**Actor:** Administrador

**Alcance:** carga inicial de comercios y actividades comerciales desde la
planilla de convenios. Es una herramienta de puesta en marcha ejecutada por
comando; no reemplaza la edición cotidiana desde el admin técnico.

**Comando de análisis:**

```bash
python manage.py importar_comercios_xlsx "data/Convenios 2026.xlsx"
```

**Comando de importación:**

```bash
python manage.py importar_comercios_xlsx "data/Convenios 2026.xlsx" --confirmar
```

**Flujo principal:**

1. El administrador aplica las migraciones pendientes y guarda la planilla
   `.xlsx` en una ruta local no versionada.
2. Ejecuta el comando sin `--confirmar`.
3. El sistema analiza la primera hoja sin modificar la base de datos.
4. Valida encabezados, campos obligatorios, longitudes, URLs completas y
   duplicados de nombre dentro de la planilla.
5. Informa cantidad de comercios, actividades comerciales, fotos, advertencias
   y errores.
6. Si no hay errores, el administrador repite el comando con `--confirmar`.
7. El sistema crea las actividades faltantes y crea o actualiza cada comercio,
   comparando nombres sin distinguir mayúsculas, acentos ni diferencias de
   espacios.
8. Las imágenes embebidas y ancladas en la columna `LOGO` se guardan en el
   campo `foto` mediante el storage configurado por Django.

**Mapeo de columnas:**

| Planilla | Modelo | Criterio |
| --- | --- | --- |
| `COMERCIO` | `Comercio.nombre` | Obligatorio. |
| `ACTIVIDAD COMERCIAL` | `Comercio.actividad_comercial` | Busca o crea `ActividadComercial` por nombre. |
| `DESCUENTO` | `Comercio.beneficio_texto` | Los porcentajes numéricos de Excel se convierten a texto, por ejemplo `0.15` a `15%`. |
| `INSTAGRAM` | `Comercio.url_presencia_web` | Conserva la URL completa de la planilla, sin agregar prefijos. Puede estar vacía. |
| `UBICACIÓN` | `Comercio.direccion` | Puede estar vacía para emprendimientos sin local físico. |
| `DESCRIPCIÓN` | `Comercio.descripcion` | Obligatoria. |
| Imagen en `LOGO` | `Comercio.foto` | Opcional; se extrae de la fila correspondiente. |

La columna `CÓDIGO` se ignora. Todos los comercios importados quedan con
`orden=0` y estado `Firmado`.

**Repetición segura:** volver a ejecutar el comando actualiza el comercio del
mismo nombre y no lo duplica. No elimina comercios ausentes de la planilla. Si
una fila no trae imagen, conserva la foto que el comercio ya tuviera.

**Errores:** si falta una columna esperada, un dato obligatorio, hay nombres
repetidos o una presencia web no es una URL `http://` o `https://`, no se
importa ninguna fila.

**Restricción técnica:** la lectura de `.xlsx` usa `openpyxl`; la validación y
extracción de imágenes usa Pillow. Las imágenes deben estar embebidas y
ancladas en la columna `LOGO`.

**Modelos afectados:** ActividadComercial, Comercio.
