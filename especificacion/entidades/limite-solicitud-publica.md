---
type: "Entidad"
title: "LimiteSolicitudPublica"
description: "Contador técnico compartido que limita acciones anónimas sobre solicitudes de asociación."
resource: "asociados.models.LimiteSolicitudPublica"
tags: [post-mvp, modelo-de-datos, seguridad, diseno-aprobado]
timestamp: 2026-08-26T00:00:00-03:00
---

# LimiteSolicitudPublica

Contador técnico usado para proteger los endpoints públicos de preinscripción.
Vive en la base compartida para que el límite no dependa de la memoria de una
instancia de Vercel.

**Campos:**

- id\*: identificador interno.
- accion\*: operación limitada, por ejemplo creación o corrección.
- clave_hash\*: resumen HMAC de la dirección o clave que identifica el límite.
- ventana_inicio\*: inicio de la ventana temporal.
- intentos\*: cantidad de intentos consumidos en esa ventana.

La combinación de acción, resumen y ventana es única. Nunca se guarda la
dirección IP, el token privado ni otra clave cruda. Estos contadores no forman
parte del historial funcional de una solicitud. Cada consumo elimina las
ventanas anteriores vencidas de esa misma acción, sin afectar otras acciones
que pueden tener ventanas diferentes.

**Presentación:** acción, inicio de ventana e intentos. Orden natural por
ventana descendente.

**Admin técnico:** consulta de soporte en modo de solo lectura. La creación y
actualización ocurren exclusivamente mediante services del dominio.

**Referencias funcionales:** ver [protección contra abuso](../reglas/solicitudes-asociacion.md#solicitud-asociacion-008--protección-contra-abuso).
