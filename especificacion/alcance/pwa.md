---
type: "Alcance"
title: "Etapa PWA"
description: "Alcance actual para instalar y usar Uni2 con conectividad limitada."
tags: [pwa, alcance, post-mvp]
timestamp: 2026-08-01T00:00:00-03:00
---

# Etapa PWA

La PWA es una etapa de evolución posterior al MVP histórico. No cambia el
alcance funcional de los dominios: permite instalar y usar mejor las
funciones existentes, pero no incorpora pedidos, pagos online ni
comunicaciones.

## Incluye

- Una única aplicación instalable llamada `UNI2`, con inicio en `/` y alcance
  para todas las rutas del sitio.
- Manifest, iconos normales y `maskable`, colores y modo `standalone`.
- Recursos visuales esenciales servidos por Uni2, sin depender de CDN para
  iniciar la aplicación.
- Pantalla general sin conexión.
- Reutilización de páginas públicas visitadas cuando sea seguro hacerlo.
- Avisos de conexión, instalación y versión disponible.
- Actualización elegida por la persona, sin recargar automáticamente un
  formulario abierto.
- Credencial mínima disponible sin conexión cuando el asociado decide
  guardarla en ese dispositivo.
- Pruebas automáticas, pruebas en dispositivos y procedimiento de rollback.

## Credencial offline incluida

La copia offline:

- requiere una acción explícita del asociado;
- dura siete días desde la última actualización correcta;
- identifica cuándo fue actualizada y que su vigencia debe validarse online;
- se elimina al cerrar sesión, al cambiar de usuario, al vencer o cuando el
  asociado elige quitarla;
- contiene sólo nombre y apellido, número de asociado, tipo, estado al momento
  de guardar y token de la credencial;
- no contiene DNI, cuotas, deuda, domicilio, correo, cookies ni tokens de
  sesión.

El comercio necesita conexión para validar la credencial. Si ambos
dispositivos están offline, el asociado puede mostrar la copia guardada pero
el comercio no puede confirmar su vigencia.

## No incluye en esta etapa

- Notificaciones push o solicitud de su permiso.
- Suscripciones push, claves VAPID o modelos para dispositivos.
- Correos transaccionales o por lote.
- Colas, reintentos o proveedores de correo.
- Background Sync.
- Formularios, cobros, validaciones o cargas encolados para enviar después.
- Cuotas, deuda, gestión o administración disponibles offline.
- Publicación en tiendas de aplicaciones.

Push y correo pertenecen a etapas posteriores y no forman parte de la
instalación ni del almacenamiento offline de la PWA. Los primeros correos se
definen en la [etapa de preinscripción y correo transaccional](preinscripcion-comunicaciones.md);
push continúa fuera de alcance.
