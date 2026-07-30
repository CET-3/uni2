---
type: "Entidad"
title: "Comercio"
description: "Comercio adherido a la mutual."
resource: "comercios.models.Comercio"
tags: [mvp, modelo-de-datos]
timestamp: 2026-07-29T00:00:00-03:00
status: "listo"
---

# Comercio

Comercio adherido a la mutual.

**Campos:**

- id\*: identificador interno del comercio.
- actividad_comercial\*: rubro o actividad principal del comercio.
- nombre\*: nombre público del comercio adherido.
- descripción\*: texto público que presenta la actividad o propuesta del comercio.
- beneficio_texto\*: texto público que describe el beneficio vigente del comercio.
- estado\*: estado del convenio con el comercio.
- orden\*: posición usada para ordenar los comercios publicados.
- foto: fotografía del comercio para mostrar en la sección Beneficios de la home. Opcional (puede no tener foto). Subida a `comercios/`.
- dirección: dirección física del comercio. Es opcional porque un emprendimiento puede no tener local o espacio de atención.
- usuario: usuario que puede iniciar sesión como este comercio.
- propietario: nombre de la persona propietaria o referente del comercio.
- fecha_convenio: fecha en que se firmó o registró el convenio.
- email: correo público o de contacto del comercio.
- teléfono: teléfono público o de contacto del comercio.
- url_presencia_web: URL pública del sitio, red social o presencia web del comercio.
- ciudad: ciudad donde se encuentra el comercio.
- provincia: provincia donde se encuentra el comercio.
- latitud: coordenada de latitud para uso futuro en mapa.
- longitud: coordenada de longitud para uso futuro en mapa.

**Estados:** pendiente, firmado, vencido, baja.

**Restricciones de datos:** puede tener usuario de acceso, usa una actividad comercial definida, guarda una descripción pública y un único beneficio como texto libre, se ordena públicamente por `orden`, puede no tener dirección física y puede guardar coordenadas para uso futuro.

**Administración:** en el MVP se carga y edita desde el admin técnico de Django. En el listado, el nombre del comercio abre el formulario de edición. El formulario muestra primero los datos principales obligatorios y ubica la descripción inmediatamente después del nombre. La puesta en marcha puede usar el [comando de importación inicial](../casos-de-uso/cu-importar-comercios-iniciales.md).

**Referencias funcionales:** ver [comercios públicos](../reglas/comercios-publicos.md), [comercios operación](../reglas/comercios-operacion.md), [credenciales](../reglas/credenciales.md), [importar comercios iniciales](../casos-de-uso/cu-importar-comercios-iniciales.md) y [validar credencial](../casos-de-uso/cu-validar-credencial.md).
