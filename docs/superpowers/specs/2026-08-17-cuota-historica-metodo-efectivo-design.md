# Método efectivo por defecto en cuotas históricas

## Objetivo

Corregir la importación histórica para que un pago marcado como realizado y
sin forma de pago informada se previsualice y se guarde como efectivo.

## Alcance

El cambio se limita a la normalización del método de pago. No modifica la
búsqueda de asociados, la clasificación de filas, los importes, los períodos ni
las reglas para valores dudosos.

## Comportamiento

Durante el análisis de cada mes:

1. se normaliza el indicador de pago;
2. se normaliza la forma de pago;
3. si el pago está realizado y la forma está vacía, se asigna
   `Pago.METODO_EFECTIVO`;
4. recién entonces se construye el registro de previsualización.

De esta manera, la previsualización guardada en sesión y el `Pago` persistido
usan el mismo valor. Una forma de pago no vacía pero dudosa continúa dejando la
fila en revisión; no se reemplaza automáticamente por efectivo.

## Pruebas y documentación

Las pruebas cubrirán el análisis y la persistencia de un pago marcado como
realizado con forma vacía. La especificación del importador histórico indicará
la presunción de efectivo.
