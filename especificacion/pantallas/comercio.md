---
type: "Pantalla"
title: "Comercio"
description: "Comercio"
tags: [mvp, pantalla]
timestamp: 2026-07-13T00:00:00-03:00
---

# Comercio

- La variante de comercio en la home muestra el nombre del comercio y los CTA `Validar credencial` y `Mi convenio`. Debajo conserva todas las secciones públicas.
- Mi convenio: ficha de solo lectura del `Comercio` vinculado a la cuenta. Agrupa datos del comercio, convenio y contacto; no recibe un ID en la URL, no muestra campos técnicos y no ofrece edición. Puede consultarse aunque el convenio esté pendiente, vencido o de baja.
- Validar credencial: formulario centrado dentro del container responsive de Bootstrap.
  Su único campo acepta el DNI o el token UUID de la credencial.
- Resultado de validación: card centrada en el mismo container, con alerta semántica y acción para volver a validar. Distingue `Credencial activa`, `Credencial inactiva` y `Credencial inválida`.
- La cámara común puede abrir la URL del QR. Si falta sesión, el login conserva
  el destino. Para una credencial encontrada, el resultado sólo expone nombre
  y apellido, tipo, curso o clasificación y estado operativo. Nunca muestra si la inactividad se debe
  a baja o deuda, ni expone cuotas, importes o DNI. Un identificador inexistente
  se informa como `Credencial inválida` y un convenio no firmado recibe un
  rechazo claro.

Las pantallas simples de esta experiencia usan `container py-5` para conservar ancho, margen lateral y separación vertical consistentes en desktop y mobile.
