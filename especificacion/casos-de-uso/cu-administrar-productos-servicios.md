---
type: "Caso de uso"
title: "CU-administrar-productos-servicios"
description: "Actor: Gestión de productos y servicios."
tags: [mvp, caso-de-uso, contenidos]
timestamp: 2026-08-10T00:00:00-03:00
---

# CU-administrar-productos-servicios

**Actor:** usuario del grupo `Gestión de productos y servicios`.

1. Entra al admin técnico.
2. Crea o selecciona una categoría.
3. Crea o modifica una categoría con descripción, imagen informativa titulada,
   contacto, orden y estado de publicación.
4. Crea o modifica un producto o servicio con descripción opcional, foto, destinatario
   escolar opcional, precios, orden y estado de publicación.
5. Si indica curso, selecciona también el ciclo. El admin ofrece los ciclos y
   años existentes en cursos activos sin repetir comisión ni turno.
6. Para el precio, carga dos importes diferentes, dos iguales, solo el importe
   de asociado o ninguno cuando se trata de un servicio sin precio.
7. Guarda y revisa su presentación pública.

**Resultado:** catálogo actualizado con evento de auditoría.

**Permisos:** categorías y productos/servicios en consulta, alta y modificación.
No incluye publicidades, comercios, usuarios ni borrado.

**Pruebas:** producto y servicio; cuatro escenarios de precio; destinatario
general, por ciclo y por curso; imágenes; orden; dato inválido; intento de crear
publicidad; usuario sin el grupo.
