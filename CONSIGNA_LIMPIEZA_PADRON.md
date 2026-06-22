# Consigna: Limpieza del padrón de asociados

Tenemos una planilla con los datos actuales de la mutual. Antes de cargarla en el sistema Uni2, necesitamos ordenar y limpiar la información.

Van a trabajar con la hoja `PADRÓN GENERAL` del archivo:

`Padrón Asociados y planilla de cobros 2026.xlsx`

El objetivo es construir una nueva hoja llamada:

`ASOCIADOS LIMPIOS`

Esa hoja debe tener estas columnas:

```text
estado_importacion
numero_asociado
apellido
nombre
dni
tipo
curso
curso_anio
curso_division
division
turno
telefono
email
direccion
observaciones
```

## Valores posibles para `estado_importacion`

Usar solo estos tres valores:

```text
IMPORTAR
REVISAR
NO IMPORTAR
```

## Criterios

Marcar como `IMPORTAR` cuando:

- tiene nombre y apellido claros
- tiene DNI cargado
- el DNI no está repetido
- el tipo es claro: asociado o adherente
- el curso es claro o puede separarse en año, división, ciclo y turno

Marcar como `REVISAR` cuando:

- falta DNI
- el DNI está repetido
- no se entiende si es asociado o adherente
- el curso está escrito de forma dudosa
- faltan datos importantes pero la persona parece real

Marcar como `NO IMPORTAR` cuando:

- la fila está vacía
- solo tiene número de socio pero no tiene persona
- parece una fila de prueba, título, aclaración o dato no válido

## Normalizaciones

En `tipo` usar solo:

```text
asociado
adherente
```

Ejemplos:

```text
Activo, activo, ACTIVO, acttivo -> asociado
Adherente, adherente, ADHERENTE, adherete -> adherente
```

En `curso`, copiar el texto original o el texto normalizado legible.

Además, completar estas cuatro columnas porque coinciden con el modelo de datos de Uni2:

```text
curso_anio
curso_division
division
turno
```

Ejemplos:

```text
Texto original: 1°1°
curso_anio: 1ro
curso_division: 1ra
division: CB
turno: TM

Texto original: 4to 2 C.S
curso_anio: 4to
curso_division: 2da
division: CS
turno: TM
```

Usar solo estos valores para `division`:

```text
CB
CS
```

Usar solo estos valores para `turno`:

```text
TM
TT
```

Si no se sabe el turno, usar `TM` como valor provisorio y aclararlo en `observaciones`.

Si dice algo como `docente`, `preceptora`, `profesor` o no se entiende, dejar vacías las columnas de curso y escribir una aclaración en `observaciones`.

## Separar nombre y apellido

La columna original viene como `Apellido/nombre`.

Pasarla a dos columnas:

```text
apellido
nombre
```

Ejemplo:

```text
Paz Giovanni
```

Debe quedar:

```text
apellido: Paz
nombre: Giovanni
```

El criterio acordado es:

- la primera palabra es el apellido
- el resto de las palabras son el nombre

Ejemplo:

```text
Sandoval Robledo Julieta Sofía
```

Debe quedar:

```text
apellido: Sandoval
nombre: Robledo Julieta Sofía
```

Si no hay al menos dos palabras, completar el dato faltante con `[completar]`, porque apellido y nombre son obligatorios para importar.

## Observaciones

Usar `observaciones` para explicar problemas, por ejemplo:

```text
DNI duplicado
Falta DNI
Curso dudoso: "1ro C.B"
Tipo dudoso: "x"
Posible docente
```

## Entrega

Cada grupo debe entregar:

1. La hoja `ASOCIADOS LIMPIOS`.
2. Un listado de casos dudosos.
3. Un resumen con:
   - cantidad de filas `IMPORTAR`
   - cantidad de filas `REVISAR`
   - cantidad de filas `NO IMPORTAR`
   - principales problemas encontrados

## Importante

No borrar datos originales. Trabajar siempre en una hoja nueva.
