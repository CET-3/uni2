---
type: "Pantalla"
title: "Comercio"
description: "Comercio"
tags: [mvp, pantalla]
timestamp: 2026-07-13T00:00:00-03:00
---

# Comercio

- La variante de comercio en la home muestra el nombre del comercio y el CTA `Validar credencial`. Debajo conserva todas las secciones públicas.
- Validar credencial: formulario centrado dentro del container responsive de Bootstrap.
  Su único campo acepta el DNI o el token UUID de la credencial.
- Resultado de validación: card centrada en el mismo container, con alerta semántica y acción para volver a validar.
- La cámara común puede abrir la URL del QR. Si falta sesión, el login conserva
  el destino. El resultado sólo expone validez, nombre y apellido, tipo y
  estado; un convenio no firmado recibe un rechazo claro.

Las pantallas simples de esta experiencia usan `container py-5` para conservar ancho, margen lateral y separación vertical consistentes en desktop y mobile.
