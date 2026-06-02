# PROMPT INICIAL PARA CODEX - UNI2

Tomá UNI2_MASTER_SPEC.md como fuente de verdad del proyecto.

## Objetivo

Implementar la primera versión (MVP) de Uni2, una plataforma de gestión para mutuales escolares basada en Django.

## Alcance

Implementar únicamente el MVP definido en UNI2_MASTER_SPEC.md.

NO implementar todavía:
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

El diseño debe quedar preparado para futuras versiones.

## Arquitectura

Utilizar apps separadas por dominio:

- usuarios
- asociados
- cuotas
- comercios
- contenidos
- contabilidad

Cada app debe contener:

- models.py
- services.py
- selectors.py
- tests/

## Organización del código

Separar responsabilidades:

- models.py → persistencia
- selectors.py → consultas
- services.py → reglas de negocio
- tests/ → pruebas

No colocar lógica de negocio en:
- views.py
- admin.py
- templates
- signals.py (salvo necesidad justificada)

## Modelos

Usar los nombres definidos en UNI2_MASTER_SPEC.md.

Agregar:

- __str__ en todos los modelos
- verbose_name y verbose_name_plural cuando corresponda
- restricciones de unicidad
- índices razonables

Utilizar constantes para choices.

## Usuarios y permisos

Utilizar User estándar de Django.

No crear custom user.

Usar Groups:

- Administradores
- Asociados
- Comercios

## Django Admin

Configurar desde el inicio:

- Colegio
- Curso
- Asociado
- InscripcionCurso
- PeriodoCuota
- Cuota
- Pago
- PagoCuota
- Comercio
- BeneficioComercio
- Beneficio
- HorarioAtencion
- Asiento

## Reglas de negocio

Implementar todas las reglas definidas en UNI2_MASTER_SPEC.md.

Especial atención a:

- Alta antes del día 15
- Alta después del día 15
- Fecha inicio cobro
- Aplicación de pagos a deuda más antigua
- Pagos parciales de cuotas
- No permitir pagos superiores a la deuda
- Asociados inactivos no generan cuotas
- Historial de cursos
- Validación de credenciales

## Seguridad

- No exponer IDs internos en URLs públicas.
- La credencial debe utilizar UUID.
- Los comercios no deben acceder a información sensible.
- Validar permisos por rol.

## Importación

Preparar un servicio o management command para importar asociados desde CSV.

No es necesaria una interfaz web en esta etapa.

## Datos iniciales

Crear mecanismos para cargar:

- CET 3
- Cursos básicos
- Grupos de usuarios
- Usuario administrador para desarrollo local

## Frontend

Utilizar:

- Templates Django
- Bootstrap 5

No utilizar React.

Priorizar funcionalidad sobre diseño visual.

## Testing

Utilizar:

- pytest
- pytest-django

Crear tests para:

### Asociados

- Alta antes del día 15
- Alta después del día 15
- Fecha inicio cobro
- Baja
- Cambio a egresado
- Creación de usuario

### Cuotas

- Generación de cuotas
- No generar cuotas duplicadas
- No generar cuotas para inactivos
- Respeto de fecha inicio cobro

### Pagos

- Pago completo
- Pago parcial
- Aplicación a deuda más antigua
- Rechazo de pagos superiores a deuda

### Comercios

- Validación de credencial activa
- Rechazo de credencial inactiva
- Beneficios vigentes
- Beneficios vencidos

### Integridad

- DNI único
- Número de asociado único
- Cuota única por asociado y período

## Entrega incremental

Antes de generar código:

1. Mostrar estructura de carpetas propuesta.
2. Mostrar plan de implementación por etapas.

Luego implementar únicamente:

- estructura del proyecto
- modelos
- migraciones
- admin
- services
- selectors
- tests

No implementar todavía vistas complejas ni frontend completo.
