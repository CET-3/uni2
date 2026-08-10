---
type: "Proceso"
title: "Documentación, capacitación y operación técnica"
description: "Responsabilidades del equipo del proyecto y de la administración técnica."
tags: [mvp, procesos, capacitacion, operacion]
timestamp: 2026-08-10T00:00:00-03:00
---

# Documentación, capacitación y operación técnica

## Documentación y capacitación

**Responsable:** grupo `Equipo del proyecto`.

Consulta la especificación y el design system para aprender, preparar pruebas y
continuar el sistema. No entra al admin técnico ni obtiene acceso a asociados,
finanzas, auditoría o contenidos por pertenecer a este grupo.

**Caso de uso:** [consultar documentación del proyecto](../casos-de-uso/cu-consultar-documentacion-proyecto.md).

## Operación técnica

**Responsable:** `Administrador de la app`, siempre con `is_superuser=True`.

Ejecuta importaciones masivas, migraciones, sincronización de grupos, despliegues
y tareas excepcionales de soporte. El grupo es una etiqueta organizativa: no
concede privilegios por sí solo.

**Caso de uso:** [sincronizar grupos](../casos-de-uso/cu-sincronizar-grupos.md).

## Secuencia de capacitación

1. Leer el proceso y el caso de uso asignado.
2. Revisar la pantalla y los permisos esperados.
3. Practicar con un perfil exclusivo del grupo en staging.
4. Probar un caso permitido y uno denegado.
5. Registrar evidencia y dudas antes de combinar grupos.
