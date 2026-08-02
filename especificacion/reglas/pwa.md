---
type: "Regla de negocio"
title: "Progressive Web App"
description: "Reglas de instalación, caché, trabajo offline y actualización."
tags: [pwa, reglas, offline, seguridad]
timestamp: 2026-08-01T00:00:00-03:00
---

# Progressive Web App

## PWA-001

Uni2 debe seguir funcionando como sitio web cuando el navegador no admita
instalación o service workers.

## PWA-002

La instalación debe ser una decisión de la persona. No se debe abrir
automáticamente un pedido de instalación.

## PWA-003

Sólo pueden persistirse como documentos generales las respuestas públicas,
anónimas y marcadas explícitamente por el servidor.

## PWA-004

Las páginas autenticadas, login, logout, administración, gestión, cuotas y
formularios no deben guardarse en Cache Storage.

## PWA-005

Una operación que necesita servidor no debe encolarse ni reenviarse al volver
la conexión. La interfaz debe informar que no fue enviada y que no quedó
pendiente.

## PWA-006

La credencial offline requiere consentimiento explícito, vence siete días
después de la última actualización correcta y debe mostrar esa fecha.

## PWA-007

La copia offline no puede incluir DNI, deuda, cuotas, domicilio, correo,
cookie, CSRF ni datos de sesión. La página autenticada completa tampoco puede
persistirse.

## PWA-008

La copia privada debe eliminarse al cerrar sesión, al detectar otra cuenta, al
vencer y cuando el asociado lo solicita.

## PWA-009

Una credencial mostrada offline no prueba vigencia. El comercio siempre debe
consultar al servidor para validarla.

## PWA-010

Una versión nueva no debe recargar automáticamente una pantalla ni
interrumpir un formulario. La actualización se aplica al aceptar el aviso o
al cerrar todas las ventanas de la versión anterior.

## PWA-011

No se debe pedir permiso de notificaciones ni crear suscripciones push durante
la instalación. Push y correo pertenecen a etapas posteriores.
