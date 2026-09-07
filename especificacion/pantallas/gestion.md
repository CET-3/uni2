---
type: "Pantalla"
title: "Gestión"
description: "Gestión"
tags: [mvp, pantalla]
timestamp: 2026-07-13T00:00:00-03:00
---

# Gestión

- La variante administrativa de la home muestra hasta dos accesos autorizados en el hero y los restantes en `Más accesos`. `Atención al asociado` tiene prioridad cuando el usuario puede consultar asociados. Los roles que solo operan mediante el admin técnico reciben ese acceso sin ver acciones de otros dominios.
- `Atención al asociado` es la consulta operativa con búsqueda y filtros. Cada fila completa contiene un único enlace accesible al detalle, con estados visibles de foco y hover; no hay columna de acciones ni cobro directo desde el listado. Los resultados priorizan `Credencial activa` o `Credencial inactiva`, muestran `Baja` sólo cuando corresponde y reservan los badges para estados. Número, DNI, curso o clasificación y tipo se presentan como datos; curso y clasificación también pueden filtrarse. El acceso de usuario puede filtrarse, pero no ocupa una columna del resultado.
- `Solicitudes de asociación` es una bandeja separada del padrón. Usa una lista
  con búsqueda y filtros por estado, tipo y fecha; distingue `Todas las
  solicitudes abiertas` de `Todas las solicitudes`, además de cada estado. No
  usa tablero de columnas. Cada fila presenta persona, documento, tipo, estado
  y fecha, abre una ficha operativa mediante un único enlace accesible y se
  reorganiza como card en mobile sin desplazamiento horizontal.
- La ficha de solicitud reúne datos, estado, historial y entregas de correo.
  En `recibida` ofrece `Aprobar datos`, `Observar` y `Cancelar solicitud`. En
  `datos_aprobados`, la acción principal es `Completar alta`; observar y
  cancelar continúan disponibles. Las acciones se ocultan o bloquean según
  estado y permisos, pero la validación definitiva siempre ocurre en el
  servidor. Las comunicaciones muestran nombres funcionales, destino, estado y
  fecha; el reenvío del correo correspondiente al estado actual vive en esa
  sección. El historial usa la línea de tiempo compartida y muestra también el
  motivo de observaciones y cancelaciones. Una solicitud con alta completada
  enlaza la ficha y el número del asociado generado.
- Observar y cancelar abren confirmaciones que exigen explicación o motivo.
  Observar enfoca inicialmente la explicación. Los breadcrumbs de estas
  acciones conservan bandeja, persona y acción sin repetir la identidad sobre
  el título. `Completar alta` muestra datos de la persona, consecuencias de la
  operación y el aviso de que no registra pagos; conserva `Volver` y, al
  confirmar, crea el asociado y sus cuotas y navega a su detalle. Una entrega
  de correo fallida queda visible y ofrece reenvío autorizado.
- La consulta conserva `Nuevo asociado` y `Exportar asociados` según permisos. La importación del padrón inicial se mantiene como acceso administrativo de puesta en marcha, pero no aparece en esta pantalla cotidiana.
- Nuevo asociado desde pantalla propia de `gestion`, sin depender del admin
  técnico. La fecha de alta toma el día local y el inicio de cobro se calcula
  automáticamente según el tipo, sin exponer ninguno de los dos campos en el
  formulario. Al guardar, genera cuotas para los períodos activos desde ese
  inicio hasta el mes actual y para los futuros cuya generación ya fue
  ejecutada; siempre continúa en el detalle del asociado creado.
- Importar padrón inicial desde planilla heredada con previsualización, reservado al superusuario Administrador de la app. La previsualización muestra la clasificación interpretada para los adherentes y deja para revisión los cargos desconocidos o las contradicciones de tipo. La pantalla incluye la acción `Crear usuarios faltantes`; también es una acción masiva reservada a ese rol. Se ejecuta por tandas y puede continuarse hasta terminar sin obligar una sola request larga.
- Importar cuotas históricas desde planilla heredada con previsualización, reservado al superusuario Administrador de la app.
- Exportar asociados en formato Uni2 desde la consulta de asociados.
- El detalle de asociado es el centro operativo: muestra datos, deuda, cuotas del año y pagos recientes. En la tabla de cuotas, `Pagada`, `Pendiente` y `Vencida` se distinguen con los mismos badges semánticos verde, amarillo y rojo de la experiencia del asociado. Su encabezado ofrece únicamente `Cobrar` y `Editar asociado`, según permisos, y una navegación secundaria vuelve a la consulta conservando sus filtros. Para quien tiene `gestion.ver_movimientos_asociado`, al pie muestra las diez operaciones de auditoría más recientes relacionadas con el asociado. El enlace de texto al historial completo filtrado aparece solamente si además posee `gestion.ver_auditoria`.
- En el detalle de asociado, los pagos recientes muestran fecha, método, total recibido y un resumen de aplicación: cuotas cubiertas y donación si existiera.
- La vista histórica de cuotas y la creación individual de usuario conservan temporalmente sus rutas y permisos, pero no tienen acceso desde el detalle mientras se diseñan sus recorridos definitivos. La auditoría filtrada se integra como información al pie del detalle.
- Cursos.
- Períodos de cuota: cada fila distingue `Todavía no generado` de `Generado el
  …`, usando la fecha y hora de la primera ejecución. La marca se presenta como
  información operativa y no forma parte del formulario de creación.
- Generar cuotas.
- Registrar pagos y donaciones exclusivamente desde el detalle de un asociado. Con deuda, la pantalla muestra cuotas pendientes ordenadas de la más vieja a la más nueva, permite seleccionar una o más cuotas a cobrar, valida que la selección sea continua desde la cuota pendiente más vieja, calcula automáticamente el mínimo a cobrar, prellena el importe recibido y registra como donación cualquier excedente. En esa tabla el saldo se muestra como importe y cada fila usa un único badge semántico compartido: amarillo para `Pendiente` y rojo para `Vencida`. Sin deuda, la acción y la pantalla se presentan como `Registrar donación`, no muestran selección de cuotas e informan que todo el importe será donado. Cada checkbox de selección tiene como nombre accesible el período de su cuota. Cancelar o completar cualquiera de los recorridos vuelve al detalle; abrir cobros sin asociado redirige a `Atención al asociado`.
- Deudores.
- Acceso al admin técnico de Django para cuentas activas con al menos un
  permiso efectivo sobre un modelo registrado, o para superusuarios. La
  bandera técnica `is_staff` no es necesaria para este acceso.
- La home oculta accesos para los que la persona no tiene permiso; los roles dedicados a convenios o publicidades pueden usar el acceso al admin sin recibir enlaces a asociados.

## Pantallas operativas de gestión

Las pantallas `Atención al asociado`, `Solicitudes de asociación`, `Nuevo asociado`, `Deudores` y `Períodos de cuota` reutilizan el mismo design system que el resto de Uni2:

- `Atención al asociado` presenta únicamente el título y las acciones autorizadas dentro de `uni2-compact-hero`: una cabecera operativa de superficie neutra que termina en escritorio con una geometría lateral de colores institucionales plenos y la reduce a una banda por debajo de `lg`; la alternativa `uni2-surface-card-brand` permanece documentada y visible en el catálogo para su validación separada;
- la búsqueda usa el título único `Buscar asociados`, sin kicker ni texto auxiliar; después de enviar filtros, `Limpiar filtros` aparece junto al botón `Buscar`, dentro del formulario, y usa el mismo tratamiento secundario con contorno que `Exportar`;
- la cantidad no se presenta como una métrica separada: el encabezado de la tabla informa `1 asociado encontrado` o la cantidad plural correspondiente; la tabla no repite instrucciones de navegación ni `Ver ficha completa` en cada fila porque el nombre ya constituye el enlace accesible;
- `Nuevo asociado`, `Deudores` y `Períodos de cuota` conservan el encabezado simple con `uni2-titulo-*`, descripción breve y `uni2-page-header-actions`, sin un hero operativo propio;
- `uni2-metric-card` para resúmenes reales y `uni2-surface-card` para búsqueda, carga, seguimiento y tablas;
- tablas con lectura densa que destacan nombre, estado, usuario, deuda o cantidad mediante `uni2-avatar` y `uni2-badge` semánticos;
- Bootstrap Icons en acciones principales y utilidades Bootstrap para grillas, alineación y adaptación responsive;
- en mobile las acciones se apilan. Las tablas de registros que usan
  `uni2-records-table` evitan el desplazamiento horizontal: conservan la tabla
  comparativa en desktop y reorganizan cada fila como una card de dos columnas
  por debajo de `md`. La consulta de asociados y la bandeja de solicitudes
  agregan enlace de fila; `Mis cuotas` reutiliza la estructura sin ser
  clickeable;
- cuando estas pantallas usan breadcrumbs, omiten `Inicio` porque el logo global ya cumple esa navegación; `Atención al asociado`, al ser una entrada operativa de primer nivel, no muestra un breadcrumb que repita su título;
- las acciones del encabezado se agrupan separadas de las métricas para evitar confundir comandos con indicadores;
- el alta manual muestra los errores de validación en una alerta destacada arriba de los campos del formulario.
- ninguna pantalla operativa usa botones `Volver`; la navegación contextual queda resuelta por breadcrumbs y por el logo global para volver al inicio.
- la ficha de asociado usa `uni2-compact-hero-with-summary` con identidad, avatar de iniciales alineado a la primera línea, título de escala controlada y un resumen de deuda calculada a la fecha; la geometría se mantiene angosta, las acciones se apilan en escritorio para liberar ancho al nombre y la deuda aparece una sola vez; por debajo de `lg`, queda entre la identidad y las acciones para conservar su prioridad en mobile;
- sus badges separan conceptos: muestran `Asociado` o `Adherente`, `Baja` únicamente ante una baja administrativa y siempre `Credencial activa` o `Credencial inactiva` según el cálculo actual. No usan el número ni `Activo`, `Vigente` o `De alta` como badge. `Estado general` muestra número, tipo, curso para asociados o clasificación para adherentes, alta e inicio de cobro y agrega fecha y motivo sólo cuando existe una baja;
- debajo de la cabecera, la ficha muestra dos paneles de igual ancho, `Estado general` y `Contacto y acceso`, envueltos en columnas Bootstrap para que sus bordes y gutters queden alineados con el hero; las secciones siguientes usan los títulos únicos `Cuotas {año}`, `Pagos recientes` e `Historial de auditoría`, sin kickers que repitan el mismo concepto;
- `Contacto y acceso` muestra dirección, email, teléfono, usuario vinculado y último acceso; los datos opcionales sin cargar se representan con `-`;
- los pares etiqueta/valor de la ficha usan `uni2-data-list`; cobros conserva clases `uni2-cobro-*` únicamente para la selección de cuotas, el resumen y la distribución de sus campos.
- el alta y la edición muestran curso o clasificación según el tipo seleccionado, deshabilitan el campo que no corresponde y exigen el visible. La edición reutiliza el hero compacto para mantener visible la identidad y el estado actual de la credencial. Presenta un único formulario, dividido mediante `fieldset` en `Identidad`, `Contacto` y `Datos administrativos`; evita textos auxiliares repetidos y no ofrece campos de baja, porque esa operación no forma parte de la edición cotidiana.
- los formularios de alta, edición, períodos y cobro usan `components/alert.html` como resumen general y muestran cada error junto al campo correspondiente.

## Auditoría de gestión

- La consulta general usa un único título y no repite un breadcrumb de un solo
  nivel. Los botones de filtro, limpieza y paginación incluyen iconos.
- Cada evento se expresa como una oración natural: actor, acción, tipo y nombre
  del objeto, y fecha y hora. El origen técnico no se muestra; el identificador
  del objeto queda como referencia secundaria `#n` y el motivo aparece en un
  renglón propio cuando existe.
- Una operación compuesta usa una sola superficie con cabecera, icono
  representativo, responsable, fecha y cantidad de eventos. Los eventos
  internos se separan mediante líneas, sin cards, iconos ni bordes de color
  anidados. La referencia UUID de la operación queda al pie. Una operación
  individual conserva su icono representativo dentro de su única cabecera.
