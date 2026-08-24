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
- Validar credencial: puesto de control `uni2-validation-station` centrado dentro
  del container responsive de Bootstrap. Una franja multicolor y un panel azul
  fuerte identifican la operación; el formulario blanco conserva un único
  campo para DNI o código UUID y una acción principal a ancho completo. En
  mobile los dos paneles se apilan sin desplazamiento horizontal.
- Resultado de validación: reutiliza el puesto de control y reemplaza el panel
  azul por verde fuerte para `Credencial activa` o rojo fuerte para
  `Credencial inactiva` y `Credencial inválida`. El estado combina color,
  icono, título e instrucción, sin depender únicamente del color. Los datos
  permitidos se muestran en el panel blanco: nombre como cabecera, DNI en texto
  secundario debajo y tipo junto con curso o clasificación en bloques de datos. La acción para volver a validar
  conserva el ancho y la jerarquía del formulario.
- La cámara común puede abrir la URL del QR. Si falta sesión, el login conserva
  el destino. Para una credencial encontrada, el resultado sólo expone nombre
  y apellido, DNI, tipo, curso o clasificación y estado operativo. Nunca muestra si la inactividad se debe
  a baja o deuda, ni expone cuotas o importes. Un identificador inexistente
  se informa como `Credencial inválida` y un convenio no firmado recibe un
  rechazo claro.

Las pantallas simples de esta experiencia usan `container py-5` para conservar ancho, margen lateral y separación vertical consistentes en desktop y mobile.
