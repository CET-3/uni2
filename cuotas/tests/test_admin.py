from django.contrib import admin

from cuotas.admin import PeriodoCuotaAdmin
from cuotas.models import PeriodoCuota


def test_periodo_admin_muestra_generado_el_como_solo_lectura():
    model_admin = PeriodoCuotaAdmin(PeriodoCuota, admin.site)

    assert "generado_el" in model_admin.readonly_fields
    assert "generado_el" in model_admin.audit_fields
