from datetime import date
from decimal import Decimal

import pytest
from django.db import connection
from django.db.migrations.executor import MigrationExecutor


@pytest.mark.django_db(transaction=True)
def test_migracion_marca_periodos_historicos_que_ya_tienen_cuotas():
    executor = MigrationExecutor(connection)
    latest_targets = executor.loader.graph.leaf_nodes()
    migration_from = [("cuotas", "0004_alter_cuota_estado")]
    migration_to = [("cuotas", "0005_periodocuota_generado_el")]
    try:
        executor.migrate(migration_from)
        old_apps = executor.loader.project_state(migration_from).apps

        CicloLectivo = old_apps.get_model("asociados", "CicloLectivo")
        Asociado = old_apps.get_model("asociados", "Asociado")
        PeriodoCuota = old_apps.get_model("cuotas", "PeriodoCuota")
        Cuota = old_apps.get_model("cuotas", "Cuota")

        ciclo = CicloLectivo.objects.create(anio=2026)
        asociado = Asociado.objects.create(
            nombre="Julia",
            apellido="Campos",
            dni="40000888",
            tipo="asociado",
            fecha_alta=date(2026, 3, 1),
            fecha_inicio_cobro=date(2026, 3, 1),
        )
        con_cuota = PeriodoCuota.objects.create(
            mes=3,
            ciclo_lectivo=ciclo,
            importe=Decimal("3000"),
            fecha_vencimiento=date(2026, 3, 10),
        )
        sin_cuota = PeriodoCuota.objects.create(
            mes=4,
            ciclo_lectivo=ciclo,
            importe=Decimal("3000"),
            fecha_vencimiento=date(2026, 4, 10),
        )
        Cuota.objects.create(asociado=asociado, periodo=con_cuota, importe=Decimal("3000"))

        executor = MigrationExecutor(connection)
        executor.migrate(migration_to)
        new_apps = executor.loader.project_state(migration_to).apps
        PeriodoCuota = new_apps.get_model("cuotas", "PeriodoCuota")

        assert PeriodoCuota.objects.get(pk=con_cuota.pk).generado_el is not None
        assert PeriodoCuota.objects.get(pk=sin_cuota.pk).generado_el is None
    finally:
        MigrationExecutor(connection).migrate(latest_targets)
