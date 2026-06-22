# Reporte preliminar de limpieza del padrón

Archivo analizado: `Padrón Asociados y planilla de cobros 2026.xlsx`

Hoja analizada: `PADRÓN GENERAL`

## Criterios aplicados

- La primera palabra de `Apellido/nombre` se tomó como apellido.
- El resto de las palabras se tomó como nombre.
- Si faltaba el nombre, se completó con `[completar]`.
- Los puntos en `C.B` y `C.S` se ignoran para deducir el ciclo.
- Si no se pueden deducir los cuatro campos del curso (`curso_anio`, `curso_division`, `division`, `turno`), la fila queda `REVISAR` y los campos faltantes quedan vacíos.
- Cuando la planilla no indica turno pero el curso está completo, se propone `TM` como valor provisorio.

## Resumen

- Filas con alguna celda cargada: 1965
- Filas con datos de persona, nombre o DNI: 534
- IMPORTAR: 422
- REVISAR: 112
- NO IMPORTAR: 1431

## Roles/cargos deducidos desde la columna curso

- docente: 19
- preceptor: 7
- directivo: 2
- padrino_mutual: 1
- biblioteca: 1
- auxiliar: 1
- particular: 1

Valores originales asociados a roles/cargos:

- `docente`: 8
- `preceptora`: 6
- `Docente`: 4
- `Profesor`: 3
- `profe`: 3
- `Preceptora`: 1
- `Padrino mutual`: 1
- `Bibliotecaria`: 1
- `portera`: 1
- `profesora`: 1
- `vicedirectora`: 1
- `Director`: 1
- `particular`: 1

## Principales motivos de revisión

- DNI duplicado: 91
- número de asociado duplicado: 10
- Falta división/comisión del curso: 10
- curso incompleto o dudoso para asociado: 10
- Falta email: 9
- Falta dirección: 9
- Falta teléfono: 5
- falta DNI: 4
- Rol/cargo en lugar de curso: "Profesor": 2
- Rol deducido: docente: 2
- tipo dudoso: 2
- Falta curso: 2
- Rol/cargo en lugar de curso: "preceptora": 1
- Rol deducido: preceptor: 1
- DNI con longitud dudosa: 498575132: 1
- Tipo dudoso: "x": 1
- Rol/cargo en lugar de curso: "portera": 1
- Rol deducido: auxiliar: 1
- DNI con longitud dudosa: 448946610: 1
- DNI con longitud dudosa: 60706082738: 1

## Ejemplos de casos para revisar

### DNI duplicado (91)

- Fila 10, socio 9: `Fernandez Martina`, DNI `52326597`, curso original `1°3°`, curso normalizado `1ro 3ra CB TM`, rol ``.
- Fila 14, socio 13: `Rojas Benjamín Ezequiel`, DNI `52327275`, curso original `1°1`, curso normalizado `1ro 1ra CB TM`, rol ``.
- Fila 17, socio 16: `Bruno Lara`, DNI `52938101`, curso original `1°3°`, curso normalizado `1ro 3ra CB TM`, rol ``.
- Fila 19, socio 18: `Izquierdo Florencia`, DNI `53015982`, curso original `1°3°`, curso normalizado `1ro 3ra CB TM`, rol ``.
- Fila 27, socio 26: `Muñoz Morales Jhoan Stiven`, DNI `96261972`, curso original `1°4°`, curso normalizado `1ro 4ta CB TM`, rol ``.

### número de asociado duplicado (10)

- Fila 2, socio 154: `Paz Giovanni`, DNI `52535594`, curso original `1°1°`, curso normalizado `1ro 1ra CB TM`, rol ``.
- Fila 151, socio 154: `Torino Gaetano Joaquin`, DNI `50873843`, curso original `1°3°`, curso normalizado `1ro 3ra CS TM`, rol ``.
- Fila 524, socio 539: `Maldonado Camila`, DNI `50505594`, curso original `1°2CS`, curso normalizado `1ro 2da CS TM`, rol ``.
- Fila 525, socio 540: `Civaroli Luz Jazmin`, DNI `52322246`, curso original `2°2°`, curso normalizado `2do 2da CS TM`, rol ``.
- Fila 526, socio 539: `Maldonado Camila`, DNI `50505584`, curso original `1°2 CS`, curso normalizado `1ro 2da CS TM`, rol ``.

### Falta división/comisión del curso (10)

- Fila 84, socio 86: `Joaquin Darosa`, DNI `52536191`, curso original `1ro C.B`, curso normalizado ``, rol ``.
- Fila 91, socio 94: `Amaro Laureano`, DNI `50024381`, curso original `2do C.S`, curso normalizado ``, rol ``.
- Fila 144, socio 147: `León lautaro joaquín`, DNI `50992691`, curso original `2doC.B`, curso normalizado ``, rol ``.
- Fila 160, socio 163: `4to 2 CS`, DNI `52534528`, curso original `1ro C.B`, curso normalizado ``, rol ``.
- Fila 174, socio 177: `Barriga Maite`, DNI `51128068`, curso original `3roC.S`, curso normalizado ``, rol ``.

### curso incompleto o dudoso para asociado (10)

- Fila 84, socio 86: `Joaquin Darosa`, DNI `52536191`, curso original `1ro C.B`, curso normalizado ``, rol ``.
- Fila 91, socio 94: `Amaro Laureano`, DNI `50024381`, curso original `2do C.S`, curso normalizado ``, rol ``.
- Fila 144, socio 147: `León lautaro joaquín`, DNI `50992691`, curso original `2doC.B`, curso normalizado ``, rol ``.
- Fila 160, socio 163: `4to 2 CS`, DNI `52534528`, curso original `1ro C.B`, curso normalizado ``, rol ``.
- Fila 174, socio 177: `Barriga Maite`, DNI `51128068`, curso original `3roC.S`, curso normalizado ``, rol ``.

### Falta email (9)

- Fila 151, socio 154: `Torino Gaetano Joaquin`, DNI `50873843`, curso original `1°3°`, curso normalizado `1ro 3ra CS TM`, rol ``.
- Fila 197, socio 200: `Reyes Paola`, DNI ``, curso original ``, curso normalizado ``, rol ``.
- Fila 450, socio 463: `Jaramillo Ulises`, DNI `52326810`, curso original `1°1`, curso normalizado `1ro 1ra CB TM`, rol ``.
- Fila 475, socio 489: `Farias Matías`, DNI `24392014`, curso original `-`, curso normalizado ``, rol ``.
- Fila 478, socio 492: `Marim Fuentes Brina`, DNI `49031341`, curso original `3°1°`, curso normalizado `3ro 1ra CS TM`, rol ``.

### Falta dirección (9)

- Fila 197, socio 200: `Reyes Paola`, DNI ``, curso original ``, curso normalizado ``, rol ``.
- Fila 334, socio 345: `Cativa Sanitago`, DNI `49029598`, curso original `3°4°`, curso normalizado `3ro 4ta CS TM`, rol ``.
- Fila 417, socio 429: `Antolini Fabricio`, DNI `48390987`, curso original `4°3°`, curso normalizado `4to 3ra CS TM`, rol ``.
- Fila 441, socio 454: `Dutrus Alma`, DNI `48946636`, curso original `3°3°`, curso normalizado `3ro 3ra CS TM`, rol ``.
- Fila 446, socio 459: `Izquierdo Florencia`, DNI `53015982`, curso original `1°3°`, curso normalizado `1ro 3ra CB TM`, rol ``.

### Falta teléfono (5)

- Fila 144, socio 147: `León lautaro joaquín`, DNI `50992691`, curso original `2doC.B`, curso normalizado ``, rol ``.
- Fila 197, socio 200: `Reyes Paola`, DNI ``, curso original ``, curso normalizado ``, rol ``.
- Fila 450, socio 463: `Jaramillo Ulises`, DNI `52326810`, curso original `1°1`, curso normalizado `1ro 1ra CB TM`, rol ``.
- Fila 489, socio 504: `Ramirez Martina`, DNI `52508747`, curso original `1ro1 CB`, curso normalizado `1ro 1ra CB TM`, rol ``.
- Fila 516, socio 531: `CADA CURSO PONGA SU COLOR CORRESPONDIENTE AL ASOCIAR PARA EVITAR CONFUSIONES!!!!!!!!`, DNI ``, curso original ``, curso normalizado ``, rol ``.

### falta DNI (4)

- Fila 114, socio 117: `Gomez Peralta Victoria`, DNI ``, curso original `preceptora`, curso normalizado ``, rol `preceptor`.
- Fila 197, socio 200: `Reyes Paola`, DNI ``, curso original ``, curso normalizado ``, rol ``.
- Fila 503, socio 518: `Arratia Leonel`, DNI ``, curso original `1ro4°Cb`, curso normalizado `1ro 4ta CB TM`, rol ``.
- Fila 516, socio 531: `CADA CURSO PONGA SU COLOR CORRESPONDIENTE AL ASOCIAR PARA EVITAR CONFUSIONES!!!!!!!!`, DNI ``, curso original ``, curso normalizado ``, rol ``.

### Rol/cargo en lugar de curso: "Profesor" (2)

- Fila 92, socio 95: `Alvarez Emanuel Alejandro`, DNI `36344251`, curso original `Profesor`, curso normalizado ``, rol `docente`.
- Fila 369, socio 381: `Emanuel Alejandro`, DNI `36344251`, curso original `Profesor`, curso normalizado ``, rol `docente`.

### Rol deducido: docente (2)

- Fila 92, socio 95: `Alvarez Emanuel Alejandro`, DNI `36344251`, curso original `Profesor`, curso normalizado ``, rol `docente`.
- Fila 369, socio 381: `Emanuel Alejandro`, DNI `36344251`, curso original `Profesor`, curso normalizado ``, rol `docente`.

