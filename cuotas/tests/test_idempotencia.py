import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from threading import Barrier

import pytest
from django.db import IntegrityError, close_old_connections, connection, transaction

from asociados.services import create_asociado
from asociados.models import CicloLectivo
from cuotas.models import Cuota, Donacion, Pago, PagoCuota, PeriodoCuota
from cuotas.services import registrar_donacion, registrar_pago


@pytest.mark.django_db
def test_reintento_donacion_no_crea_otro_ingreso():
    asociado = create_asociado(nombre="Ana", apellido="Prueba", dni="43210001", tipo="asociado", fecha_alta=date(2026, 9, 1))
    datos = dict(asociado=asociado, fecha=date(2026, 9, 5), importe="100", metodo="efectivo", clave_operacion=uuid.uuid4())
    registrar_donacion(**datos)
    with pytest.raises(ValueError, match="ya fue registrada"):
        registrar_donacion(**datos)
    assert Pago.objects.count() == 1
    assert Donacion.objects.count() == 1
    registrar_donacion(**{**datos, "clave_operacion": uuid.uuid4()})
    assert Pago.objects.count() == 2


@pytest.mark.django_db
def test_base_rechaza_clave_pago_duplicada_y_error_no_la_consume():
    asociado = create_asociado(nombre="Ana", apellido="Prueba", dni="43210002", tipo="asociado", fecha_alta=date(2026, 9, 1))
    datos = dict(asociado=asociado, fecha=date(2026, 9, 5), importe="100", metodo="efectivo", clave_operacion=uuid.uuid4())
    with pytest.raises(ValueError, match="mayor que cero"):
        registrar_donacion(**{**datos, "importe": "0"})
    assert Pago.objects.count() == 0
    registrar_donacion(**datos)
    with pytest.raises(IntegrityError), transaction.atomic():
        Pago.objects.create(**datos)
    assert Pago.objects.count() == 1


@pytest.mark.django_db(transaction=True)
def test_cobros_concurrentes_no_aplican_dos_veces_la_deuda():
    if connection.vendor != "postgresql":
        pytest.skip("La concurrencia con bloqueo de filas requiere PostgreSQL")
    asociado = create_asociado(nombre="Ana", apellido="Prueba", dni="43210003", tipo="asociado", fecha_alta=date(2026, 9, 1))
    periodo = PeriodoCuota.objects.create(
        ciclo_lectivo=CicloLectivo.objects.create(anio=2026), mes=9,
        importe="100", fecha_vencimiento=date(2026, 9, 10),
    )
    cuota = Cuota.objects.create(asociado=asociado, periodo=periodo, importe="100")
    barrier = Barrier(2)

    def cobrar():
        close_old_connections()
        try:
            barrier.wait(timeout=10)
            try:
                registrar_pago(
                    asociado=asociado, fecha=date(2026, 9, 5), importe="100",
                    metodo="efectivo", cuotas_ids=[cuota.pk], clave_operacion=uuid.uuid4(),
                )
                return True
            except ValueError:
                return False
        finally:
            close_old_connections()

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(lambda _: cobrar(), range(2)))
    assert sorted(results) == [False, True]
    assert Pago.objects.count() == PagoCuota.objects.count() == 1
    cuota.refresh_from_db()
    assert cuota.importe_pagado == 100
