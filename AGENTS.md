# AGENTS.md

## Contexto del proyecto

Uni2 es una plataforma de gestión para mutuales escolares basada en Django.

La fuente funcional principal del proyecto es:

- `UNI2_MASTER_SPEC.md`
- `especificacion/index.html`

Si hay diferencias entre implementación y documentación, hay que reducir esa brecha. No dejar decisiones nuevas solamente en el código o en commits.

## Objetivo

Implementar y mantener el MVP de Uni2 respetando el alcance funcional definido en la especificación.

No implementar todavía:

- Pedidos
- Stock
- PagoPedido
- Tickets
- Mensajería
- PWA
- Notificaciones push
- Pago online
- Mapa de comercios
- Contabilidad avanzada

## Principio clave de documentación

Todo cambio relevante tiene que quedar escrito en la especificación.

Esto incluye:

- cambios de arquitectura
- nuevas decisiones funcionales
- cambios de navegación
- nuevas pantallas
- cambios de comportamiento
- restricciones técnicas que afecten cómo se usa o mantiene el sistema

Si una tarea modifica cómo se organiza el proyecto o cómo funciona una parte del sistema, actualizar la especificación en el mismo trabajo. No dejarlo para después.

## Cómo comunicar

La usuaria principal es programadora, pero este proyecto lo van a continuar estudiantes secundarios.

Por eso, al trabajar en este repo:

- explicar siempre qué se está haciendo y por qué
- preferir cambios fáciles de seguir antes que soluciones demasiado “mágicas”
- dejar estructura clara y nombres explícitos
- evitar mover lógica sin dejar trazabilidad
- cuando se refactoriza, explicar la nueva ubicación de cada responsabilidad
- cuando se cambia arquitectura, reflejarlo en la especificación

Pensar cada cambio como algo que otra persona en formación va a tener que leer, entender y continuar.

## Arquitectura actual

Las apps se separan por dominio o experiencia:

- `web`: home y páginas públicas
- `usuarios`: autenticación, login/logout, roles y redirecciones por perfil
- `gestion`: backoffice para staff
- `asociados`: experiencia del asociado autenticado
- `comercios`: experiencia del comercio autenticado
- `cuotas`: cuotas, pagos y deuda
- `contenidos`: beneficios que consume la web
- `contabilidad`: cuentas y asientos

## Organización del código

Separar responsabilidades:

- `models.py` → persistencia
- `selectors.py` → consultas
- `services.py` → reglas de negocio
- `views.py` → composición HTTP y renderizado
- `tests/` → pruebas

No colocar lógica de negocio en:

- `views.py`
- `admin.py`
- `templates`
- `signals.py`, salvo necesidad muy justificada

## Reglas de implementación

- Usar apps separadas por dominio.
- Mantener URLs y namespaces coherentes con la responsabilidad de cada app.
- No mezclar experiencia pública con backoffice.
- No mezclar autenticación con lógica operativa de gestión si puede vivir en otra app.
- Priorizar código legible antes que abstracciones prematuras.
- Cuando una estructura deje de ser clara, refactorizarla y documentarlo.

## Modelos

- Usar los nombres definidos en la especificación.
- Agregar `__str__` en todos los modelos.
- Agregar `verbose_name` y `verbose_name_plural` cuando corresponda.
- Agregar restricciones de unicidad e índices razonables.
- Usar constantes para `choices`.

## Usuarios y permisos

- Usar `User` estándar de Django.
- No crear custom user.
- Usar `Groups` para roles.
- Validar permisos por rol y por contexto.

## Admin de Django

El admin de Django se considera una herramienta técnica y de soporte.

- No debe ser la única interfaz de operación si un flujo necesita UX propia.
- Las tareas frecuentes de staff deberían vivir en `gestion`.
- Si se agrega algo importante al admin, evaluar si también debe figurar en la especificación o en el backoffice.

## Frontend

- Usar Templates Django.
- Usar Bootstrap 5.
- No usar React.
- Priorizar funcionalidad y claridad.
- En pantallas internas, cuidar desktop y mobile.

## Testing

- Usar `pytest` y `pytest-django`.
- Agregar o actualizar tests cuando cambie comportamiento.
- Si no se puede correr la suite, dejar asentado por qué.

## Entrega de cambios

Antes de cambios grandes:

1. explicar la estructura actual encontrada
2. explicar qué se va a mover o cambiar
3. explicar el criterio de separación

Después de cambios grandes:

1. resumir qué cambió
2. indicar archivos clave
3. indicar riesgos o puntos pendientes
4. actualizar la especificación

## Commits

- Escribir los mensajes de commit en castellano.
- Preferir mensajes breves, claros y descriptivos.

## Regla final

El proyecto no solo tiene que funcionar: tiene que quedar entendible, enseñable y documentado.
