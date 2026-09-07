from decimal import Decimal

import pytest

from asociados.models import Curso
from contenidos.admin import ProductoServicioAdmin, ProductoServicioInline
from contenidos.forms import CategoriaProductoServicioAdminForm, ProductoServicioAdminForm
from contenidos.models import CategoriaProductoServicio, ProductoServicio


@pytest.fixture
def categoria(db):
    return CategoriaProductoServicio.objects.create(nombre="Cuadernillos")


def crear_curso(*, anio="1ro", curso="1ra", ciclo=Curso.DIVISION_CB, turno=Curso.TURNO_TM, activo=True):
    return Curso.objects.create(
        anio=anio,
        curso=curso,
        division=ciclo,
        turno=turno,
        activo=activo,
    )


def datos_formulario(categoria, **cambios):
    datos = {
        "categoria": categoria.pk,
        "nombre": "Matemática",
        "descripcion": "Cuadernillo de actividades.",
        "ciclo_destinatario": Curso.DIVISION_CB,
        "curso_destinatario": "1ro",
        "precio_asociados": "100.00",
        "precio_no_asociados": "150.00",
        "activo": "on",
        "orden": "1",
    }
    datos.update(cambios)
    return datos


def test_formulario_deduplica_ciclo_y_anio_sin_turno_ni_comision(db):
    crear_curso()
    crear_curso(curso="2da", turno=Curso.TURNO_TT)

    form = ProductoServicioAdminForm()

    assert list(form.fields["ciclo_destinatario"].choices) == [
        ("", "---------"),
        (Curso.DIVISION_CB, "Ciclo Básico"),
    ]
    assert list(form.fields["curso_destinatario"].choices) == [
        ("", "---------"),
        ("1ro", "1ro"),
    ]


def test_formulario_acepta_combinacion_activa(categoria):
    crear_curso()
    form = ProductoServicioAdminForm(data=datos_formulario(categoria))

    assert form.is_valid(), form.errors


def test_formulario_rechaza_combinacion_inexistente(categoria):
    crear_curso()
    crear_curso(anio="2do", ciclo=Curso.DIVISION_CS)
    form = ProductoServicioAdminForm(
        data=datos_formulario(categoria, curso_destinatario="2do"),
    )

    assert not form.is_valid()
    assert form.errors["curso_destinatario"] == ["El ciclo y el curso elegidos no corresponden a un curso activo."]


def test_formulario_rechaza_curso_sin_ciclo(categoria):
    crear_curso()
    form = ProductoServicioAdminForm(
        data=datos_formulario(categoria, ciclo_destinatario="", curso_destinatario="1ro"),
    )

    assert not form.is_valid()
    assert form.errors["curso_destinatario"] == ["No puede indicar un curso sin seleccionar el ciclo."]


def test_formulario_acepta_producto_sin_descripcion(categoria):
    crear_curso()
    form = ProductoServicioAdminForm(
        data=datos_formulario(categoria, descripcion=""),
    )

    assert form.is_valid(), form.errors


def test_formulario_conserva_combinacion_actual_inactiva(categoria):
    curso = crear_curso()
    producto = ProductoServicio.objects.create(
        categoria=categoria,
        nombre="Matemática",
        descripcion="Cuadernillo de actividades.",
        ciclo_destinatario=Curso.DIVISION_CB,
        curso_destinatario="1ro",
        precio_asociados=Decimal("100"),
        precio_no_asociados=Decimal("150"),
    )
    curso.activo = False
    curso.save(update_fields=["activo"])

    form = ProductoServicioAdminForm(
        data=datos_formulario(categoria),
        instance=producto,
    )

    assert (Curso.DIVISION_CB, "Ciclo Básico") in list(form.fields["ciclo_destinatario"].choices)
    assert ("1ro", "1ro") in list(form.fields["curso_destinatario"].choices)
    assert form.is_valid(), form.errors


def test_admin_e_inline_usan_formulario_de_destinatarios():
    assert ProductoServicioAdmin.form is ProductoServicioAdminForm
    assert ProductoServicioInline.form is ProductoServicioAdminForm
    assert "foto" in ProductoServicioInline.fields


def test_formulario_categoria_explica_la_etiqueta_de_icono_y_enlaza_bootstrap_icons():
    form = CategoriaProductoServicioAdminForm()

    ayuda = str(form.fields["etiqueta_icono"].help_text)

    assert "Nombre de un ícono de Bootstrap Icons" in ayuda
    assert "https://icons.getbootstrap.com/" in ayuda
    assert '<a href="https://icons.getbootstrap.com/"' in ayuda


def test_admin_audita_los_nuevos_campos():
    assert {"foto", "ciclo_destinatario", "curso_destinatario"}.issubset(ProductoServicioAdmin.audit_fields)
