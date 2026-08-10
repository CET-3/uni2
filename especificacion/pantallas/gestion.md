---
type: "Pantalla"
title: "Gestión"
description: "Gestión"
tags: [mvp, pantalla]
timestamp: 2026-07-13T00:00:00-03:00
---

# Gestión

- Dashboard simple con accesos a las tareas del MVP permitidas para el usuario.
- Consulta de asociados con búsqueda y filtros.
- Nuevo asociado desde pantalla propia de `gestion`, sin depender del admin técnico. Al guardar, genera cuotas iniciales para períodos existentes y, si el usuario tiene permiso para cobrar, continúa en la pantalla de cobro con el asociado preseleccionado.
- Importar padrón inicial desde planilla heredada con previsualización, reservado al superusuario Administrador de la app. El dashboard y la pantalla de importación incluyen la acción `Crear usuarios faltantes`; también es una acción masiva reservada a ese rol. Se ejecuta por tandas y puede continuarse hasta terminar sin obligar una sola request larga.
- Importar cuotas históricas desde planilla heredada con previsualización, reservado al superusuario Administrador de la app.
- Exportar asociados en formato Uni2 desde la consulta de asociados.
- Detalle de asociado.
- En el detalle de asociado, los pagos recientes muestran fecha, método, total recibido y un resumen de aplicación: cuotas cubiertas y donación si existiera.
- Ver todas las cuotas de un asociado desde su detalle.
- Crear usuario para asociado.
- Cursos.
- Períodos de cuota.
- Generar cuotas.
- Registrar pago desde un asociado seleccionado en la consulta de asociados. La pantalla de cobro muestra cuotas pendientes ordenadas de la más vieja a la más nueva, permite seleccionar una o más cuotas a cobrar, valida que la selección sea continua desde la cuota pendiente más vieja, calcula automáticamente el mínimo a cobrar, prellena el importe recibido y registra como donación cualquier excedente. Cada checkbox de selección tiene como nombre accesible el período de su cuota, para que pueda identificarse al navegar el formulario con tecnologías asistivas.
- Deudores.
- Acceso al admin técnico de Django solo para usuarios con `is_staff`.
- El dashboard oculta accesos para los que la persona no tiene permiso; los roles dedicados a convenios o publicidades pueden usar el acceso al admin sin recibir enlaces a asociados.
