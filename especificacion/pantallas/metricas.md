---
type: "Pantalla"
title: "Métricas"
description: "Evolución y gestión de la mutual."
tags: [gestion, metricas, pantalla]
timestamp: 2026-09-10T00:00:00-03:00
---

# Métricas

Entrada `/gestion/metricas/`, desde la home administrativa según permiso.
Filtros GET con errores visibles: período, comparación y padrón. Mantiene la
maqueta aprobada y el design system productivo, no su CSS exploratorio.

- Cuatro cards: activos al cierre, cuotas generadas, cobrado de esas cuotas,
  cumplimiento. Altas/bajas/neto y pendiente en una línea secundaria.
- Franjas compactas Quiénes somos y Solicitudes de asociación.
- Ingresos por fecha efectiva separados de cobranza de cuotas.
- Dos gráficos Chart.js: padrón (activos o altas/bajas) y generado/cobrado mensual.
- Situaciones a atender hoy: deuda y grupos de cuotas vencidas.
- Desplegables de solicitudes, clasificación de adherentes, antigüedad de deuda,
  oferta de comercios y tablas equivalentes a los gráficos.
- Advertencias por inconsistencias; no se presentan como datos históricos
  confiables las fechas que el modelo ya no conserva.

Bootstrap 5 y base.html; cards e iconos del design system. Las variaciones
usan color más flecha/texto. Los datos JSON se transfieren con json_script;
Chart.js sólo dibuja y navega. Sin React ni servicios frontend. La copia local
de Chart.js permite no depender de un CDN para cargar la pantalla, aunque los
datos privados requieren conexión. Los gráficos cambian con el tema y tienen
alternativa tabular utilizable sin JavaScript.
Las columnas numéricas (cantidades, importes y porcentajes), con sus encabezados,
se alinean a la derecha. Fechas, nombres y descripciones quedan a la izquierda.

`/gestion/metricas/detalle/` conserva los filtros y pagina 25 registros. Desde
altas/bajas, estados de solicitudes, grupos de deuda o clasificación actual se
accede a las fichas existentes con sus permisos. El gráfico de altas y bajas
enlaza al segmento elegido cuando el usuario puede consultar personas.

Ver [reglas y fórmulas](../reglas/metricas.md).
