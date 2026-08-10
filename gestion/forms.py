from django import forms
from django.utils import timezone

from auditoria.models import EventoAuditoria
from auditoria.presentacion import etiqueta_entidad
from auditoria.selectors import listar_entidades_auditadas
from asociados.models import Asociado
from asociados.models import Curso
from asociados.services import create_asociado
from cuotas.models import Pago, PeriodoCuota


class FiltroAuditoriaForm(forms.Form):
    actor = forms.CharField(required=False, label="Persona que realizó la acción")
    objeto = forms.CharField(required=False, label="Objeto modificado")
    accion = forms.ChoiceField(
        required=False,
        choices=[("", "Todas las acciones")] + EventoAuditoria.ACCIONES,
        label="Acción",
    )
    entidad = forms.ChoiceField(required=False, choices=(), label="Entidad")
    objeto_id = forms.CharField(required=False, label="ID exacto del objeto")
    origen = forms.ChoiceField(
        required=False,
        choices=[("", "Todos los orígenes")] + EventoAuditoria.ORIGENES,
        label="Origen",
    )
    fecha_desde = forms.DateField(required=False, label="Desde")
    fecha_hasta = forms.DateField(required=False, label="Hasta")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["actor"].widget.attrs.update(
            {
                "class": "form-control form-control-sm",
                "placeholder": "Nombre, apellido o usuario",
            }
        )
        self.fields["objeto"].widget.attrs.update(
            {
                "class": "form-control form-control-sm",
                "placeholder": "Nombre, descripción o ID",
            }
        )
        self.fields["accion"].widget.attrs.update({"class": "form-select form-select-sm"})
        entidades = listar_entidades_auditadas()
        entidad_solicitada = self.data.get("entidad", "") if self.is_bound else ""
        if entidad_solicitada and entidad_solicitada not in entidades:
            entidades.append(entidad_solicitada)
        self.fields["entidad"].choices = [("", "Todas las entidades")] + [
            (entidad, etiqueta_entidad(entidad)) for entidad in entidades
        ]
        self.fields["entidad"].widget.attrs.update({"class": "form-select form-select-sm"})
        self.fields["objeto_id"].widget.attrs.update({"class": "form-control form-control-sm"})
        self.fields["origen"].widget.attrs.update({"class": "form-select form-select-sm"})
        for field_name in ("fecha_desde", "fecha_hasta"):
            self.fields[field_name].widget.attrs.update(
                {"class": "form-control form-control-sm", "type": "date"}
            )


class CobroCuotaForm(forms.Form):
    asociado_id = forms.IntegerField(widget=forms.HiddenInput)
    cuotas_ids = forms.MultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple)
    fecha = forms.DateField(initial=timezone.localdate)
    importe = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)
    metodo = forms.ChoiceField(choices=Pago.METODOS)
    observaciones = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 3}))

    def __init__(self, *args, cuotas_queryset=None, **kwargs):
        super().__init__(*args, **kwargs)
        cuotas_queryset = list(cuotas_queryset or [])
        self.fields["cuotas_ids"].choices = [(str(cuota.id), str(cuota.id)) for cuota in cuotas_queryset]
        self.fields["cuotas_ids"].required = bool(cuotas_queryset)
        self.fields["fecha"].widget.attrs.update({"class": "form-control", "type": "date"})
        self.fields["importe"].widget.attrs.update({"class": "form-control", "step": "0.01"})
        self.fields["metodo"].widget.attrs.update({"class": "form-select"})
        self.fields["observaciones"].widget.attrs.update({"class": "form-control"})

    def clean_asociado_id(self):
        asociado_id = self.cleaned_data["asociado_id"]
        if not Asociado.objects.filter(id=asociado_id).exists():
            raise forms.ValidationError("El asociado seleccionado no existe.")
        return asociado_id

    def clean_cuotas_ids(self):
        return [int(cuota_id) for cuota_id in self.cleaned_data["cuotas_ids"]]


class PeriodoCuotaForm(forms.ModelForm):
    class Meta:
        model = PeriodoCuota
        fields = ["mes", "ciclo_lectivo", "importe", "importe_recargo_mes", "importe_recargo_mes_siguiente", "fecha_vencimiento", "activo"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ["mes", "importe", "importe_recargo_mes", "importe_recargo_mes_siguiente", "fecha_vencimiento"]:
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
            "direccion",
            "tipo",
            "curso_actual",
            "fecha_alta",
            "fecha_inicio_cobro",
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
            if field_name in {"fecha_alta", "fecha_inicio_cobro"}:
                field.widget.attrs.update({"type": "date"})


class AsociadoAltaForm(forms.ModelForm):
    class Meta:
        model = Asociado
        fields = [
            "nombre",
            "apellido",
            "dni",
            "email",
            "telefono",
            "direccion",
            "tipo",
            "curso_actual",
            "fecha_alta",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_bound:
            self.initial.setdefault("fecha_alta", timezone.localdate())
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.update({"class": "form-select"})
            else:
                field.widget.attrs.update({"class": "form-control"})
            if field_name == "fecha_alta":
                field.widget.attrs.update({"type": "date"})

    def save(self, commit=True, actor=None):
        data = self.cleaned_data
        return create_asociado(
            nombre=data["nombre"],
            apellido=data["apellido"],
            dni=data["dni"],
            tipo=data["tipo"],
            fecha_alta=data["fecha_alta"],
            curso_actual=data["curso_actual"],
            email=data["email"],
            telefono=data["telefono"],
            direccion=data["direccion"],
            actor=actor,
        )


class ImportarPadronAsociadosForm(forms.Form):
    archivo = forms.FileField(
        label="Planilla heredada de padrón",
        help_text='Debe ser un archivo .xlsx con la hoja "PADRÓN GENERAL". Este formato se usa para la puesta en marcha.',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["archivo"].widget.attrs.update({"class": "form-control", "accept": ".xlsx"})

    def clean_archivo(self):
        archivo = self.cleaned_data["archivo"]
        if not archivo.name.lower().endswith(".xlsx"):
            raise forms.ValidationError("La planilla debe ser un archivo .xlsx.")
        return archivo


class ImportarCuotasHistoricasForm(forms.Form):
    archivo = forms.FileField(
        label="Planilla heredada de cuotas",
        help_text='Debe ser un archivo .xlsx con la hoja "COBRO CUOTAS SOCIALES".',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["archivo"].widget.attrs.update({"class": "form-control", "accept": ".xlsx"})

    def clean_archivo(self):
        archivo = self.cleaned_data["archivo"]
        if not archivo.name.lower().endswith(".xlsx"):
            raise forms.ValidationError("La planilla debe ser un archivo .xlsx.")
        return archivo


class FiltroAsociadosForm(forms.Form):
    q = forms.CharField(required=False, label="Buscar", widget=forms.TextInput())
    estado = forms.ChoiceField(required=False, choices=[("", "Todos")] + list(Asociado.ESTADOS), label="Estado")
    tipo = forms.ChoiceField(required=False, choices=[("", "Todos")] + list(Asociado.TIPOS), label="Tipo")
    curso_actual = forms.ModelChoiceField(
        required=False,
        queryset=Curso.objects.select_related().order_by("division", "anio", "curso", "turno"),
        empty_label="Todos los cursos",
        label="Curso actual",
    )
    usuario = forms.ChoiceField(
        required=False,
        choices=[
            ("", "Todos"),
            ("con", "Con usuario"),
            ("sin", "Sin usuario"),
        ],
        label="Usuario vinculado",
    )
    deuda = forms.ChoiceField(
        required=False,
        choices=[
            ("", "Todos"),
            ("con", "Con deuda"),
            ("sin", "Sin deuda"),
        ],
        label="Deuda",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["q"].widget.attrs.update({"class": "form-control", "placeholder": "DNI, número, apellido o nombre"})
        self.fields["estado"].widget.attrs.update({"class": "form-select"})
        self.fields["tipo"].widget.attrs.update({"class": "form-select"})
        self.fields["curso_actual"].widget.attrs.update({"class": "form-select"})
        self.fields["usuario"].widget.attrs.update({"class": "form-select"})
        self.fields["deuda"].widget.attrs.update({"class": "form-select"})
