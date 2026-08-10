from django import template

from config.formatting import formatear_moneda


register = template.Library()


@register.filter
def moneda(valor):
    return formatear_moneda(valor)
