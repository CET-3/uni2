from django import forms

from asociados.models import Curso

from .models import ProductoServicio


class ProductoServicioAdminForm(forms.ModelForm):
    ciclo_destinatario = forms.ChoiceField(required=False)
    curso_destinatario = forms.ChoiceField(required=False)

    class Meta:
        model = ProductoServicio
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["categoria"].widget.attrs["autofocus"] = True

        combinaciones_activas = list(
            Curso.objects.filter(activo=True)
            .values_list("division", "anio")
            .distinct()
            .order_by("division", "anio")
        )
        ciclos_activos = {ciclo for ciclo, _anio in combinaciones_activas}
        anios_activos = {anio for _ciclo, anio in combinaciones_activas}

        if self.instance and self.instance.pk:
            if self.instance.ciclo_destinatario:
                ciclos_activos.add(self.instance.ciclo_destinatario)
            if self.instance.curso_destinatario:
                anios_activos.add(self.instance.curso_destinatario)

        etiquetas_ciclo = dict(Curso.DIVISIONES)
        self.fields["ciclo_destinatario"].choices = [
            ("", "---------"),
            *((ciclo, etiquetas_ciclo.get(ciclo, ciclo)) for ciclo, _etiqueta in Curso.DIVISIONES if ciclo in ciclos_activos),
        ]
        self.fields["curso_destinatario"].choices = [
            ("", "---------"),
            *((anio, anio) for anio in sorted(anios_activos)),
        ]

    def clean(self):
        datos = super().clean()
        ciclo = datos.get("ciclo_destinatario")
        curso = datos.get("curso_destinatario")

        if curso and not ciclo:
            self.add_error("curso_destinatario", "No puede indicar un curso sin seleccionar el ciclo.")
            return datos

        if not curso:
            return datos

        es_combinacion_actual = bool(
            self.instance
            and self.instance.pk
            and ciclo == self.instance.ciclo_destinatario
            and curso == self.instance.curso_destinatario
        )
        existe_combinacion_activa = Curso.objects.filter(
            activo=True,
            division=ciclo,
            anio=curso,
        ).exists()
        if not es_combinacion_actual and not existe_combinacion_activa:
            self.add_error(
                "curso_destinatario",
                "El ciclo y el curso elegidos no corresponden a un curso activo.",
            )

        return datos
