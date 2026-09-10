# Prueba manual de Métricas

Usar datos ficticios locales. No crear cobros de ejemplo en Producción.

1. Aplicar migraciones. Administrador de la mutual ve Métricas; Atención al
   asociado no recibe ese permiso automáticamente. Comprobar acceso directo.
2. Alternar Hoy, Esta semana, Este mes, Mes anterior, Este año, Últimos 12 meses
   y Personalizado. Revisar límites, comparación y fechas inválidas/futuras.
3. Comparar septiembre con agosto: una baja de septiembre debe seguir activa
   al cierre de agosto. Alta/baja en el día del cierre respeta ese límite.
4. Cuota agosto pagada septiembre: figura en cobrado de agosto y en ingresos
   de septiembre. Recargos/donaciones no inflan cumplimiento por capital.
5. Importado histórico: sí cobra cuota, no es ingreso fechado. Cuota bonificada
   a cero y período vacío no producen división por cero.
6. Revisar quiénes somos, porcentajes de adherentes y sus clasificaciones.
   Elegir un padrón no convierte la franja actual en una historia de tipos.
7. Solicitud agosto completada septiembre: cohorte agosto, estado actual. El
   resumen no es la bandeja completa de pendientes de Atención diaria.
8. Ver deuda de 1, 2 y 3+ cuotas, recargos y vencimientos a 30/31/60/61 días.
   Cambiar el rango no cambia la deuda de hoy; cambiar padrón sí puede hacerlo.
9. Abrir listados desde métricas y gráficos; volver conserva filtros. Probar
   permisos insuficientes, parámetros inválidos y paginación.
10. Desktop/móvil, claro/oscuro, teclado y sin JavaScript: tablas accesibles,
    sin importes cortados. Sin conexión no se muestran datos cacheados.

Pruebas de cálculo: `DB_ENGINE=sqlite .venv/bin/pytest gestion/tests/test_metricas.py gestion/tests/test_periodos_metricas.py -q`.
