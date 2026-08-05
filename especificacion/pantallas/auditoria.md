---
type: "Pantalla"
title: "Auditoría de gestión"
description: "Consulta de solo lectura del historial de operaciones de Uni2."
tags: [mvp, gestion, diseno-aprobado, pendiente]
timestamp: 2026-08-01T00:00:00-03:00
---

# Auditoría de gestión

## Estado

Pantalla aprobada y pendiente de implementación.

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

Las filas que comparten `operacion_id` se presentan agrupadas o con una
identificación común. Esto permite entender como una sola operación un cobro o
una importación que afectó varios objetos.

## Filtros

- intervalo de fechas;
- actor;
- acción;
- entidad;
- origen;
- identificador o texto del objeto;
- `operacion_id` cuando se ingrese desde el detalle de una operación.

Los resultados se ordenan del más reciente al más antiguo y usan paginación.
No se implementa exportación en la primera versión.

## Detalle de cambios

El detalle presenta por campo:

```text
Campo          Valor anterior       Valor nuevo
Teléfono       1234                 5678
Curso actual   2do 1ra CB TM        3ro 1ra CB TM
```

Los valores excluidos por seguridad se muestran como `Valor protegido`. Nunca
se muestran contraseñas, tokens o secretos.

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
- El detalle desplegable informa su estado mediante `aria-expanded`.
- Los cambios no se comunican solamente mediante color.

