---
type: "Caso de uso"
title: "CU-ver-convenio-propio"
description: "Actor: Comercio autenticado."
tags: [mvp, caso-de-uso, comercio, convenios]
timestamp: 2026-08-21T00:00:00-03:00
---

# CU-ver-convenio-propio

**Actor:** Comercio autenticado.

**Objetivo:** consultar en modo lectura los datos del comercio y del convenio
que la mutual mantiene vinculados a la propia cuenta.

**Precondiciones:** el usuario pertenece al rol Comercio y tiene un registro
`Comercio` vinculado.

**Flujo principal:**

1. El comercio entra a su experiencia desde la home.
2. Elige `Mi convenio`, junto a la acción `Validar credencial`.
3. El sistema obtiene el comercio desde el vínculo del usuario autenticado, sin
   recibir un identificador de comercio en la URL.
4. Muestra en modo lectura:
   - comercio: foto, nombre, actividad, descripción y propietario;
   - convenio: estado, fecha y beneficio acordado;
   - contacto: email, teléfono, dirección, ciudad, provincia y presencia web.
5. El comercio puede volver al inicio. La pantalla no permite editar ni abrir
   el admin técnico.

**Datos no visibles:** ID interno, usuario vinculado, orden de publicación,
latitud y longitud.

**Campos opcionales:** se muestran como `Sin informar` cuando el rótulo aporta
contexto. Si no existe una foto, se omite. La presencia web se abre de manera
segura en una pestaña nueva.

**Permisos y estados:** cada usuario sólo puede consultar su propio comercio.
La consulta está disponible para convenios pendientes, firmados, vencidos o de
baja; el estado firmado se exige para validar credenciales, no para ver los
datos propios.

**Situaciones especiales:** un usuario sin sesión o sin rol Comercio no puede
acceder. Si tiene el rol pero no existe un comercio vinculado, el sistema
informa el problema y vuelve a la home.

**Reglas relacionadas:** [Comercios — operación](../reglas/comercios-operacion.md).

**Modelo afectado:** Comercio.
