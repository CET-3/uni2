from django.apps import apps


def etiqueta_entidad(entidad):
    """Convierte la etiqueta técnica de un modelo en un nombre visible."""

    if "." in entidad:
        app_label, model_name = entidad.split(".", 1)
        model = apps.get_model(app_label, model_name)
        if model is not None:
            return str(model._meta.verbose_name).capitalize()
    return str(entidad).rsplit(".", 1)[-1]
