from django import forms

from .periodos import resolver_periodo_atencion
from .permissions import GESTION_VER_COBROS_EQUIPO


class FiltroAtencionDiariaForm(forms.Form):
    periodo = forms.ChoiceField(label="Fecha del pago", choices=[
        ("hoy", "Hoy"), ("ayer", "Ayer"),
        ("esta_semana", "Esta semana"), ("personalizado", "Rango de fechas"),
    ])
    operador = forms.ChoiceField(label="Registrados por", choices=[("propios", "Mis cobros")])
    desde = forms.DateField(label="Desde", required=False,
        widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"))
    hasta = forms.DateField(label="Hasta", required=False,
        widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"))

    def __init__(self, data=None, *, user, hoy=None, **kwargs):
        equipo = user.has_perm(GESTION_VER_COBROS_EQUIPO)
        # Completar sólo parámetros ausentes: un valor inválido no se reemplaza.
        values = data.copy() if data is not None else {}
        values.setdefault("periodo", "hoy")
        values.setdefault("operador", "equipo" if equipo else "propios")
        super().__init__(values, **kwargs)
        self.hoy = hoy
        if equipo:
            self.fields["operador"].choices = [("equipo", "Todo el equipo"), ("propios", "Mis cobros")]
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-select" if isinstance(field, forms.ChoiceField) else "form-control"

    def clean(self):
        datos = super().clean()
        if not self.errors:
            try:
                datos["intervalo"] = resolver_periodo_atencion(
                    datos["periodo"], datos.get("desde"), datos.get("hasta"), hoy=self.hoy,
                )
            except ValueError as exc:
                raise forms.ValidationError(str(exc)) from exc
        return datos
