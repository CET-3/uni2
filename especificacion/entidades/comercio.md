---
type: "Entidad"
title: "Comercio"
description: "Comercio adherido a la mutual."
resource: "comercios.models.Comercio"
tags: [mvp, modelo-de-datos]
timestamp: 2026-06-22T00:00:00-03:00
status: "listo"
---

# Comercio

Comercio adherido a la mutual.

**Campos:**

- id\*: identificador interno del comercio.
- actividad_comercial\*: rubro o actividad principal del comercio.
- nombre\*: nombre público del comercio adherido.
- beneficio_texto\*: texto público que describe el beneficio vigente del comercio.
- estado\*: estado del convenio con el comercio.
- orden\*: posición usada para ordenar los comercios publicados.
- flyer_disponible\*: indica si existe un flyer o pieza de difusión disponible.
- dirección\*: dirección física del comercio.
- usuario: usuario que puede iniciar sesión como este comercio.
- propietario: nombre de la persona propietaria o referente del comercio.
- fecha_convenio: fecha en que se firmó o registró el convenio.
- notas: notas internas para seguimiento administrativo.
- email: correo público o de contacto del comercio.
- teléfono: teléfono público o de contacto del comercio.
- url_presencia_web: URL pública del sitio, red social o presencia web del comercio.
- ciudad: ciudad donde se encuentra el comercio.
- provincia: provincia donde se encuentra el comercio.
- latitud: coordenada de latitud para uso futuro en mapa.
- longitud: coordenada de longitud para uso futuro en mapa.

**Estados:** pendiente, firmado, vencido, baja.

**Restricciones de datos:** puede tener usuario de acceso, usa una actividad comercial definida, guarda un único beneficio como texto libre, se ordena públicamente por `orden` y puede guardar coordenadas para uso futuro.

**Referencias funcionales:** ver [comercios públicos](../reglas/comercios-publicos.md), [comercios operación](../reglas/comercios-operacion.md), [credenciales](../reglas/credenciales.md) y [validar credencial](../casos-de-uso/cu-validar-credencial.md).
