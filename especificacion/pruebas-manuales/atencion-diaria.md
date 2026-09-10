# Prueba manual de Atención diaria

Usar datos de ejemplo en local o staging, no registrar cobros ficticios en Producción.

1. Aplicar migraciones y ejecutar `sincronizar_grupos --apply` si corresponde a
   la puesta en marcha del ambiente. Ingresar con Atención al asociado y abrir
   Atención diaria desde la home administrativa.
2. Registrar desde las fichas un pago en efectivo que cubra dos cuotas
   (incluida una atrasada) y una donación. Registrar otro por billetera.
   Comprobar que efectivo + billetera = total y que las donaciones ya están
   incluidas. El tablero no ofrece un botón propio de registro de cobros.
3. Revisar que cada pago aparezca una sola vez, aunque cubra varias cuotas.
   Abrir su detalle y comprobar importes por cuota y donación, operador y fechas.
4. Alternar Hoy, Ayer y Esta semana; la semana empieza el lunes. Probar rango
   inclusivo, rango sin pagos, fechas invertidas, faltantes y futuras.
5. Con Atención al asociado sólo se ofrecen cobros propios. Con Administrador
   de la mutual se puede elegir Todo el equipo. Un pago sin operador queda
   incluido únicamente en el alcance del equipo.
6. Crear un pago con fecha anterior al día de carga. El importe figura por su
   fecha efectiva; el aviso de cargas permite revisarlo por el día de creación.
   Un pago histórico sin creación auditada no debe inventar fecha de carga.
7. Comprobar que solicitudes pendientes incluyan entradas antiguas sin importar
   el rango seleccionado y que cada enlace conserve el estado. Las altas sí
   usan el período, pero no el filtro de cobrador.
8. Con más de 25 pagos, comprobar páginas, conservación de filtros y totales de
   toda la consulta. Probar usuario sin permiso y acceso directo a pago ajeno.
9. Revisar a 390 px y en escritorio, temas claro/oscuro, navegación por teclado
   y sin JavaScript. Las filas se apilan y los importes mantienen dos decimales.
10. Sin conexión, la PWA debe usar su respuesta offline habitual sin presentar
    el tablero ni datos de pagos cacheados.
11. Con pagos de la importación histórica dentro del rango, comprobar que se
    muestran separados como `Pagos históricos sin fecha de cobro confirmada`,
    fuera de total, efectivo, billetera, cantidades, composición y listado de
    cobros. Cambiar operador/rango debe filtrar ese resumen también. Las cuotas
    y sus aplicaciones deben seguir pagadas, sin alterar la deuda.

Pruebas automatizadas principales:
`DB_ENGINE=sqlite .venv/bin/pytest gestion/tests/test_atencion_diaria.py -q`.

Prueba opcional en navegador real:
`DB_ENGINE=sqlite .venv/bin/pytest tests/frontend/test_atencion_browser.py -q`.
Requiere Chrome/Chromium y Node 22 o superior (WebSocket nativo); se puede indicar
el ejecutable de Node mediante `UNI2_BROWSER_NODE`. Son herramientas de prueba,
no dependencias de la aplicación. Usa datos sintéticos y guarda capturas en el
directorio temporal de pytest. Comprueba escritorio/móvil, ambos temas mediante
el selector real, importes, filtros y navegación al detalle del pago.
