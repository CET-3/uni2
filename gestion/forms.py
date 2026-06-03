from django import forms
from django.utils import timezone

from asociados.models import Asociado
from cuotas.models import Pago, PeriodoCuota


class CobroCuotaForm(forms.Form):
    asociado_id = forms.IntegerField(widget=forms.HiddenInput)
    fecha = forms.DateField(initial=timezone.localdate)
    importe = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)
    metodo = forms.ChoiceField(choices=Pago.METODOS)
    observaciones = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 3}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["fecha"].widget.attrs.update({"class": "form-control", "type": "date"})
        self.fields["importe"].widget.attrs.update({"class": "form-control", "step": "0.01"})
        self.fields["metodo"].widget.attrs.update({"class": "form-select"})
        self.fields["observaciones"].widget.attrs.update({"class": "form-control"})

    def clean_asociado_id(self):
        asociado_id = self.cleaned_data["asociado_id"]
        if not Asociado.objects.filter(id=asociado_id).exists():
            raise forms.ValidationError("El asociado seleccionado no existe.")
        return asociado_id


class PeriodoCuotaForm(forms.ModelForm):
    class Meta:
        model = PeriodoCuota
        fields = ["mes", "ciclo_lectivo", "importe", "importe_recargo_mora", "fecha_vencimiento", "activo"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ["mes", "importe", "importe_recargo_mora", "fecha_vencimiento"]:
            self.fields[field_name].widget.attrs.update({"class": "form-control"})
        self.fields["fecha_vencimiento"].widget.attrs.update({"type": "date"})
        self.fields["ciclo_lectivo"].widget.attrs.update({"class": "form-select"})
        self.fields["activo"].widget.attrs.update({"class": "form-check-input"})


class AsociadoGestionForm(forms.ModelForm):
    class Meta:
        model = Asociado
        fields = [
            "nombre",
            "apellido",
            "dni",
            "email",
            "telefono",
            "tipo",
            "curso_actual",
            "estado",
            "fecha_alta",
            "fecha_inicio_cobro",
            "fecha_baja",
            "motivo_baja",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({"class": "form-check-input"})
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({"class": "form-select"})
            else:
                field.widget.attrs.update({"class": "form-control"})
            if field_name in {"fecha_alta", "fecha_inicio_cobro", "fecha_baja"}:
                field.widget.attrs.update({"type": "date"})

    def clean(self):
        cleaned_data = super().clean()
        estado = cleaned_data.get("estado")
        fecha_baja = cleaned_data.get("fecha_baja")
        motivo_baja = cleaned_data.get("motivo_baja")
        if estado == Asociado.ESTADO_INACTIVO and not fecha_baja:
            self.add_error("fecha_baja", "La baja requiere fecha de baja.")
        if estado == Asociado.ESTADO_INACTIVO and not motivo_baja:
            self.add_error("motivo_baja", "La baja requiere motivo.")
        if estado != Asociado.ESTADO_INACTIVO:
            cleaned_data["fecha_baja"] = None
            cleaned_data["motivo_baja"] = ""
        return cleaned_data

