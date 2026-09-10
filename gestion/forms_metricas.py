from django import forms

from .periodos import comparar_periodo, resolver_periodo_metricas


class FiltroMetricasForm(forms.Form):
    periodo = forms.ChoiceField(label="Período", choices=[
        ("hoy", "Hoy"), ("esta_semana", "Esta semana"), ("este_mes", "Este mes"),
        ("mes_anterior", "Mes anterior"), ("este_anio", "Este año"),
        ("ultimos_12_meses", "Últimos 12 meses"), ("personalizado", "Personalizado"),
    ])
    comparar = forms.ChoiceField(label="Comparar con", choices=[
        ("anterior", "Período anterior"), ("anio_anterior", "Mismo período del año anterior"), ("sin", "Sin comparación"),
    ])
    tipo = forms.ChoiceField(label="Padrón", choices=[("todos", "Todos"), ("asociado", "Asociados"), ("adherente", "Adherentes")])
    desde = forms.DateField(label="Desde", required=False, widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"))
    hasta = forms.DateField(label="Hasta", required=False, widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"))

    def __init__(self, data=None, **kwargs):
        values = data.copy() if data is not None else {}
        for key, default in (("periodo", "este_anio"), ("comparar", "anio_anterior"), ("tipo", "todos")):
            values.setdefault(key, default)
        super().__init__(values, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-select" if isinstance(field, forms.ChoiceField) else "form-control"

    def clean(self):
        data = super().clean()
        if not self.errors:
            try:
                data["intervalo"] = resolver_periodo_metricas(data["periodo"], data.get("desde"), data.get("hasta"))
                data["comparacion"] = comparar_periodo(data["intervalo"], data["comparar"], data["periodo"])
            except (ValueError, OverflowError) as error:
                raise forms.ValidationError(str(error)) from error
        return data
