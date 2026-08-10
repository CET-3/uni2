---
type: "Pantalla"
title: "Progressive Web App"
description: "Estados globales de instalación, conexión, actualización y credencial offline."
tags: [pwa, pantalla, responsive, accesibilidad]
timestamp: 2026-08-01T00:00:00-03:00
---

# Progressive Web App

## Instalación

La acción “Instalar Uni2” aparece sólo cuando existe una forma de instalación
aplicable. No tapa contenido ni se muestra como modal automático. En iOS puede
abrir instrucciones breves para usar Compartir y “Agregar a pantalla de
inicio”.

## Estado de conexión

Un aviso accesible informa al pasar offline y al recuperar la conexión. Usa
`aria-live`, no depende sólo del color y no bloquea la lectura.

## Sin conexión

La pantalla general incluye:

- identidad de Uni2;
- título “Sin conexión”;
- explicación breve;
- acción para volver a intentar;
- enlace al inicio;
- acceso a Mi credencial cuando existe una copia privada vigente.

No muestra navbar personalizada, nombre de usuario, deuda ni datos recuperados
de una respuesta autenticada.

## Credencial offline

Con conexión, Mi credencial ofrece:

- explicación del almacenamiento en el dispositivo;
- acción explícita para guardar;
- duración de siete días;
- fecha de última actualización y vencimiento;
- acción para quitar.

Sin conexión, la copia vigente muestra sus campos mínimos, su antigüedad y un
aviso destacado:

> Esta copia puede estar desactualizada. El comercio necesita conexión para
> confirmar la vigencia.

Una copia vencida o de otra cuenta nunca se representa.
El QR online y el guardado codifican la misma URL absoluta
`/credenciales/<token UUID>/`. Mostrarla offline no evita que la validación
necesite una sesión de comercio y conexión con el servidor.

## Actualización

El aviso “Hay una versión nueva de Uni2” permite aplicar la actualización
cuando la persona esté lista. No toma foco inesperadamente ni recarga por sí
solo.

## Aplicación instalada

- Respeta el tema claro u oscuro.
- Adapta el color del navegador o ventana al tema.
- Respeta áreas seguras de pantallas con recorte.
- Funciona en orientación vertical y horizontal.
- Respeta `prefers-reduced-motion`.
- Mantiene navegación y foco por teclado.
