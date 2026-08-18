# Alineación del rediseño del PR #42 con el design system

## Objetivo

Conservar las mejoras de jerarquía visual, legibilidad y adaptación mobile del
PR #42 sin crear un segundo sistema visual dentro de Uni2.

El resultado debe ser fácil de revisar y continuar por estudiantes. Cada
decisión visual compartida debe pertenecer al design system; una pantalla no
puede inventar otra escala de tipografía, color, radio, sombra o espaciado.

## Contexto

El PR #42 mejora varias pantallas de gestión y autoservicio, pero incorpora
familias amplias de clases (`uni2-ops-*`, `uni2-member-*` y
`uni2-access-*`) que se superponen con componentes existentes. También crea
presentaciones propias para métricas, cards, alertas, títulos y accesos.

La rama del PR apunta a `staging` y ya contiene el `staging` vigente. La suite
combinada pasa antes de esta alineación. Se guardó una línea base local con
ocho pantallas en desktop de 1440 px y mobile de 390 px, usando datos
ficticios.

## Decisión

Se aplica el criterio **reutilización primero y extensión mínima**:

1. Se busca una solución en Bootstrap 5 o en el inventario productivo Uni2.
2. Si un componente existente cubre la responsabilidad, se reutiliza.
3. Si le falta una capacidad general, se amplía su contrato y su muestra en
   `/design-system/`.
4. Solo se crea un componente cuando existe un faltante real y reutilizable.
5. Una clase específica del dominio queda permitida únicamente cuando expresa
   una estructura que no tendría sentido fuera de ese flujo.

No se conserva la apariencia del PR píxel por píxel. Se conserva su mejora de
organización, jerarquía, densidad, responsive y claridad operativa.

## Matriz de decisiones sobre los patrones del PR

| Patrón incorporado por el PR | Decisión | Destino |
|---|---|---|
| `uni2-ops-page` | Eliminar cuando solo aporte un fondo nuevo | Container y fondo global existentes |
| `uni2-ops-hero*` | Eliminar | Encabezado Bootstrap, `uni2-titulo-*`, `uni2-section-kicker` y `uni2-page-header-actions` |
| `uni2-ops-panel*` | Reemplazar y ampliar de forma mínima | `card`, `uni2-surface-card` y modificadores de acento azul, verde, amarillo y rojo |
| `uni2-ops-metric*` | Reemplazar y ampliar | `uni2-metric-card`, con variantes `info`, `success`, `warning` y `danger` |
| `uni2-ops-badge*` | Renombrar y reducir | `uni2-badge` con variantes `info`, `success`, `warning` y `danger` |
| `uni2-ops-avatar*` | Generalizar | Nuevo `uni2-avatar` con modificadores de color |
| `uni2-ops-table` | Eliminar si no aporta comportamiento | `table-responsive`, `table-soft` y utilidades Bootstrap |
| `uni2-ops-actions*` | Eliminar | `uni2-page-header-actions` y utilidades Bootstrap |
| `uni2-form-error-summary` | Eliminar | `components/alert.html` más errores junto a cada campo |
| `uni2-record-list` | Generalizar | Nuevo `uni2-data-list` para pares etiqueta/valor |
| `uni2-access-*` | Eliminar | `uni2-service-card` y grilla Bootstrap |
| `uni2-member-hero*` | Eliminar | Encabezado simple según la especificación de asociado |
| `uni2-member-page` | Eliminar | Fondo global y container existentes |
| `uni2-member-metrics` | Eliminar | Grilla Bootstrap con `uni2-metric-card` |
| `uni2-member-credential` y `uni2-member-card-mark` | Eliminar | Componente `uni2-credential` existente, sin marca decorativa duplicada |
| `uni2-member-offline-copy` | Eliminar | Utilidades flex de Bootstrap |
| `uni2-member-dues-table` | Eliminar | `table-responsive` y `table-soft` |
| `uni2-cobro-*` | Conservar solo lo estructural | Clases específicas para selección y resumen del cobro |
| `uni2-period-*` | Conservar solo lo estructural | Clases específicas para importes y generación de períodos |

La matriz se actualizará durante la implementación si aparece una clase del PR
que no esté enumerada. Ninguna familia nueva queda aceptada implícitamente.

## Contrato de los componentes nuevos o ampliados

Cada componente que sobreviva debe quedar registrado en cuatro lugares:

1. CSS productivo con una clase raíz `uni2-*`, elementos internos y
   modificadores explícitos.
2. Catálogo `/design-system/` con una muestra real en tema claro y oscuro.
3. Inventario en `especificacion/arquitectura/design-system-conceptos.md`.
4. Explicación de responsabilidad y límites en
   `especificacion/arquitectura/design-system.md` cuando cambie el contrato.

Cada entrada debe responder:

- qué problema visual resuelve;
- cuándo debe usarse;
- cuándo no debe usarse;
- qué clase raíz necesita;
- qué modificadores admite;
- de qué tokens y componentes depende.

No se crea un template reusable salvo que exista una unidad visual con API
propia. Las composiciones simples permanecen en Bootstrap y en el template de
la pantalla.

## Tokens y CSS

- Tipografía: los títulos usan `uni2-titulo-principal`,
  `uni2-titulo-seccion` o `uni2-titulo-componente`. Los componentes no crean
  otra escala global mediante selectores propios de `h1` o `h2`.
- Color: texto y estados usan tokens de rol. Los colores de marca se reservan
  para identidad y variantes explícitas.
- Contraste: fondos verdes y amarillos usan un token de texto apto para fondo
  brillante; azul y rojo oscuro usan texto claro.
- Radios y sombras: se reutilizan `--radius-*` y `--shadow-*`. Un literal solo
  queda si es estrictamente local y no se repite.
- Responsive: se usan utilidades Bootstrap y los cortes `991.98px`,
  `767.98px` y `575.98px`. No se agregan breakpoints intermedios.
- Movimiento: toda transición decorativa respeta `prefers-reduced-motion`.
- Organización: el CSS continúa en `uni2-design-system.css`, ordenado según la
  estructura documentada. No se agregan hojas paralelas ni bloques duplicados
  por pantalla.

## Aplicación por área

### Gestión

Los listados, formularios, ficha, cobro, deudores y períodos conservan las
mejoras de agrupación, textos de ayuda, métricas útiles y adaptación mobile.
Se componen con encabezados existentes, surface cards, métricas compartidas,
breadcrumbs, tablas y acciones Bootstrap.

### Asociado

Credencial y cuotas mantienen el container responsive y el encabezado simple
definido por la especificación. Pueden reutilizar métricas y surface cards, pero
no introducen otro hero. La credencial conserva QR, consentimiento offline,
token, estados y acciones existentes.

### Home

Los accesos adicionales vuelven a usar `uni2-service-card` y la grilla de
Bootstrap. No se crea un lanzador visual paralelo.

## Datos y comportamiento

Se conservan `cuotas_total` y `cuotas_con_saldo` porque aportan información
real a la pantalla. No se modifican modelos ni se generan migraciones.

La refactorización visual no puede cambiar permisos, destinos, submits,
filtros, cálculo de deuda, selección de cuotas, navegación contextual,
credencial offline ni formato monetario.

## Errores y accesibilidad

- El resumen general de un formulario usa `components/alert.html`.
- El error concreto se muestra junto al campo correspondiente.
- Los mensajes urgentes usan `role="alert"`; el contenido informativo no se
  convierte innecesariamente en una región viva.
- Cada checkbox repetido conserva un nombre asociado a su cuota.
- Las filas navegables mantienen un solo enlace y foco visible.
- Los colores siempre se acompañan con texto, importe, icono o etiqueta.
- Tablas y acciones siguen siendo utilizables a 390 px.

## Verificación

### Automatizada

- Suite completa con SQLite.
- Checks existentes de PostgreSQL en CI.
- Tests de vistas para acciones, permisos, textos y estados funcionales.
- Tests estructurales del design system para asegurar que:
  - los nuevos componentes figuren en el catálogo y el inventario;
  - no sobrevivan familias reemplazadas sin una justificación documentada;
  - no se creen nuevas escalas tipográficas o breakpoints arbitrarios;
  - las alertas productivas sigan usando el componente compartido.

### Visual

Se repiten las mismas ocho vistas con datos ficticios en desktop de 1440 px y
mobile de 390 px. La comparación debe registrar para cada pantalla:

- qué mejora del PR se conservó;
- qué efecto decorativo se simplificó;
- qué componente existente reemplazó al patrón nuevo;
- si hubo cambios de altura, densidad o desplazamiento horizontal;
- resultado en tema claro y oscuro.

Las capturas completas son artefactos locales de revisión y no se agregan al
repositorio. El resultado de la comparación se resume por escrito en el PR.

## Criterios de aceptación

- No hay una segunda familia general de componentes paralela al catálogo.
- Todo componente nuevo o ampliado puede identificarse en el diff mediante la
  matriz y tiene muestra, contrato e inventario.
- El diff final de `uni2-design-system.css` agrega como máximo 500 líneas
  respecto de `origin/staging`, menos de la mitad de las 1.145 líneas agregadas
  originalmente por el PR, y no duplica decisiones existentes.
- Las pantallas conservan sus acciones, permisos, información y comportamiento.
- Desktop, mobile, tema claro, tema oscuro y navegación por teclado quedan
  verificados.
- La revisión del PR permite distinguir claramente qué se reutilizó, qué se
  amplió, qué se agregó y qué se eliminó del design system.
