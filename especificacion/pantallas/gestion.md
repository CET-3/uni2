---
type: "Pantalla"
title: "Gestión"
description: "Gestión"
tags: [mvp, pantalla]
timestamp: 2026-07-13T00:00:00-03:00
---

# Gestión

- La variante administrativa de la home muestra hasta dos accesos autorizados en el hero y los restantes en `Más accesos`. `Atención al asociado` tiene prioridad cuando el usuario puede consultar asociados. Los roles que solo operan mediante el admin técnico reciben ese acceso sin ver acciones de otros dominios.
- `Atención al asociado` es la consulta operativa con búsqueda y filtros. Cada fila completa contiene un único enlace accesible al detalle, con estados visibles de foco y hover; no hay columna de acciones ni cobro directo desde el listado.
- La consulta conserva `Nuevo asociado` y `Exportar asociados` según permisos. La importación del padrón inicial se mantiene como acceso administrativo de puesta en marcha, pero no aparece en esta pantalla cotidiana.
- Nuevo asociado desde pantalla propia de `gestion`, sin depender del admin técnico. Al guardar, genera cuotas iniciales para períodos existentes y siempre continúa en el detalle del asociado creado.
- Importar padrón inicial desde planilla heredada con previsualización, reservado al superusuario Administrador de la app. La pantalla de importación incluye la acción `Crear usuarios faltantes`; también es una acción masiva reservada a ese rol. Se ejecuta por tandas y puede continuarse hasta terminar sin obligar una sola request larga.
- Importar cuotas históricas desde planilla heredada con previsualización, reservado al superusuario Administrador de la app.
- Exportar asociados en formato Uni2 desde la consulta de asociados.
- El detalle de asociado es el centro operativo: muestra datos, deuda, cuotas del año y pagos recientes. Su encabezado ofrece únicamente `Cobrar` y `Editar asociado`, según permisos, y una navegación secundaria vuelve a la consulta conservando sus filtros. Para quien tiene `gestion.ver_movimientos_asociado`, al pie muestra las diez operaciones de auditoría más recientes relacionadas con el asociado. El enlace de texto al historial completo filtrado aparece solamente si además posee `gestion.ver_auditoria`.
- En el detalle de asociado, los pagos recientes muestran fecha, método, total recibido y un resumen de aplicación: cuotas cubiertas y donación si existiera.
- La vista histórica de cuotas y la creación individual de usuario conservan temporalmente sus rutas y permisos, pero no tienen acceso desde el detalle mientras se diseñan sus recorridos definitivos. La auditoría filtrada se integra como información al pie del detalle.
- Cursos.
- Períodos de cuota.
- Generar cuotas.
- Registrar pagos y donaciones exclusivamente desde el detalle de un asociado. Con deuda, la pantalla muestra cuotas pendientes ordenadas de la más vieja a la más nueva, permite seleccionar una o más cuotas a cobrar, valida que la selección sea continua desde la cuota pendiente más vieja, calcula automáticamente el mínimo a cobrar, prellena el importe recibido y registra como donación cualquier excedente. Sin deuda, la acción y la pantalla se presentan como `Registrar donación`, no muestran selección de cuotas e informan que todo el importe será donado. Cada checkbox de selección tiene como nombre accesible el período de su cuota. Cancelar o completar cualquiera de los recorridos vuelve al detalle; abrir cobros sin asociado redirige a `Atención al asociado`.
- Deudores.
- Acceso al admin técnico de Django solo para usuarios con `is_staff`.
- La home oculta accesos para los que la persona no tiene permiso; los roles dedicados a convenios o publicidades pueden usar el acceso al admin sin recibir enlaces a asociados.

## Pantallas operativas de gestión

Las pantallas `Atención al asociado`, `Nuevo asociado`, `Deudores` y `Períodos de cuota` reutilizan el mismo design system que el resto de Uni2:

- encabezado simple con `uni2-titulo-*`, descripción breve y `uni2-page-header-actions`, sin un hero operativo propio;
- `uni2-metric-card` para resúmenes reales y `uni2-surface-card` para búsqueda, carga, seguimiento y tablas;
- tablas con lectura densa que destacan nombre, estado, usuario, deuda o cantidad mediante `uni2-avatar` y `uni2-badge` semánticos;
- Bootstrap Icons en acciones principales y utilidades Bootstrap para grillas, alineación y adaptación responsive;
- en mobile las acciones se apilan y las tablas conservan desplazamiento horizontal.
- los breadcrumbs de estas pantallas omiten `Inicio` porque el logo global ya cumple esa navegación;
- las acciones del encabezado se agrupan separadas de las métricas para evitar confundir comandos con indicadores;
- el alta manual muestra los errores de validación en una alerta destacada arriba de los campos del formulario.
- ninguna pantalla operativa usa botones `Volver`; la navegación contextual queda resuelta por breadcrumbs y por el logo global para volver al inicio.
- la ficha de asociado usa los mismos componentes compartidos: encabezado con identidad, métricas de deuda, acciones permitidas, paneles de estado/contacto/cuenta corriente, cuotas y pagos recientes.
- los pares etiqueta/valor de la ficha usan `uni2-data-list`; cobros conserva clases `uni2-cobro-*` únicamente para la selección de cuotas, el resumen y la distribución de sus campos.
- los formularios de alta, edición, períodos y cobro usan `components/alert.html` como resumen general y muestran cada error junto al campo correspondiente.
