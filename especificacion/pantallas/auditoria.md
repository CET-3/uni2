---
type: "Pantalla"
title: "Auditoría de gestión"
description: "Consulta de solo lectura del historial de operaciones de Uni2."
tags: [mvp, gestion, implementado]
timestamp: 2026-08-09T00:00:00-03:00
---

# Auditoría de gestión

## Estado

Pantalla implementada.

## Acceso

- URL prevista: `/gestion/auditoria/`.
- Requiere autenticación y permiso `gestion.ver_auditoria`.
- El acceso sin permiso responde 403.
- No presenta botones para crear, editar o eliminar eventos.

## Listado

El listado muestra:

- fecha y hora;
- actor o proceso;
- acción;
- tipo de entidad;
- objeto afectado;
- origen;
- motivo cuando exista;
- acceso al detalle de cambios.

Los eventos que comparten `operacion_id` se presentan dentro de una sola
tarjeta de operación. La agrupación es solamente visual: cada evento conserva
y muestra su frase, entidad, identificador, origen y detalle de cambios. No se
resume ni se elimina información del historial persistido. Las operaciones que
contienen un único evento mantienen la tarjeta simple.

La cabecera de una operación compuesta usa un título de negocio obtenido de
sus eventos, por ejemplo `Cobro de cuotas`, `Alta de asociado`, `Generación de
cuotas` o `Creación y vinculación de usuario`. Cuando no existe una descripción
específica usa `Cambios relacionados`. El UUID queda como referencia técnica
secundaria y no compite con el título.

## Filtros

- intervalo de fechas;
- persona que realizó la acción mediante nombre, apellido o nombre de usuario;
- objeto modificado mediante descripción o identificador parcial;
- acción;
- entidad mediante un desplegable construido a partir de las entidades que ya
  tienen eventos registrados;
- origen;
- identificador exacto del objeto;
- el `operacion_id` se muestra en las operaciones compuestas para facilitar su
  identificación técnica.

La versión actual separa la búsqueda de la persona que realizó la acción de la
búsqueda del objeto modificado. También permite filtrar por acción, entidad,
identificador exacto del objeto, origen y fechas desde/hasta. La presentación de
cada evento mantiene una oración con actor, acción, objeto y fecha. El actor se
muestra con el nombre y apellido actuales cuando la cuenta sigue vinculada. Si
no están cargados o la cuenta ya no existe, usa el nombre registrado en
`actor_etiqueta`. Debajo aparecen entidad, identificador, origen y los cambios
visibles en una tarjeta compacta con color lateral según la acción.

Los resultados se ordenan del más reciente al más antiguo y se paginan por
operación, no por evento. Así los eventos relacionados nunca quedan divididos
entre dos páginas. Un filtro selecciona las operaciones que tengan al menos un
evento coincidente; una vez encontrada la operación, se muestran todos sus
eventos para no recortar su trazabilidad. No se implementa exportación en la
primera versión.

## Detalle de cambios

El detalle presenta por campo:

```text
Campo          Valor anterior       Valor nuevo
Teléfono       1234                 5678
Curso actual   2do 1ra CB TM        3ro 1ra CB TM
```

Los valores excluidos por seguridad se muestran como `Valor protegido`. Nunca
se muestran contraseñas, tokens o secretos.

En una modificación se muestran valor anterior, flecha y valor nuevo. En una
creación no se repite un valor anterior vacío: la sección `Datos cargados`
muestra solamente valores nuevos y omite campos vacíos. En desktop usa dos
columnas y en pantallas angostas pasa a una sola columna. No hay acordeones ni
textos del tipo “1 cambio realizado”: cuando una operación es compuesta, sus
eventos se agrupan en una tarjeta y permanecen visibles.

En desktop, anterior y nuevo forman una secuencia compacta junto a la etiqueta
del campo; no se distribuyen en extremos opuestos de la tarjeta. Los valores
largos pueden envolver. En mobile la secuencia se apila para conservar la
legibilidad. La etiqueta del campo se alinea con la primera línea del cambio,
también cuando alguno de los valores ocupa varias líneas.

Los eventos financieros usan frases de negocio: `registró un pago`, `aplicó un
importe a la cuota` y `actualizó la cuota`. No muestran como título las
representaciones técnicas de `Pago` o `PagoCuota`. Fechas, métodos e importes se
presentan con etiquetas legibles; `registrado_por` se omite del detalle porque
duplica al actor de la oración. Los importes respetan el formato monetario
general `$ 1.000,00`. Las aplicaciones `PagoCuota` conservan además su sección
de datos para que una operación agrupada no pierda ninguna relación registrada.

La jerarquía tipográfica reserva semibold para el actor, el objeto y las
etiquetas de campo. Metadatos y valores permanecen con peso normal; no se usa
negrita simultáneamente en todos los elementos de la tarjeta.

Si el objeto todavía existe y la persona tiene permiso para consultarlo, su
descripción puede enlazar al detalle correspondiente. Si fue eliminado o ya no
es accesible, el evento conserva la descripción sin ofrecer un enlace roto.

## Historial contextual

Las pantallas de detalle prioritarias podrán mostrar una sección `Historial`
con los mismos datos, filtrados por entidad e identificador. La primera
integración será el detalle de asociado; pagos y comercios se incorporarán en
etapas posteriores.

## Estados vacíos y casos especiales

- Sin resultados: explicar que no hay eventos para los filtros elegidos.
- Actor eliminado o no disponible: mostrar `actor_etiqueta`.
- Dato anterior a la auditoría: informar que no existe historia anterior.
- Operación automática: mostrar la identificación del proceso y su origen.
- Objeto eliminado excepcionalmente: mostrar su descripción histórica.

## Responsive y accesibilidad

- En desktop puede utilizar una tabla.
- En mobile los eventos deben conservar fecha, actor, acción y objeto sin
  depender de scroll horizontal para comprender lo esencial.
- Los controles de filtros tienen etiquetas visibles.
- La agrupación usa estructura semántica de sección y encabezado; no requiere
  interacción para acceder a sus eventos.
- Los cambios no se comunican solamente mediante color.
