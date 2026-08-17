from types import SimpleNamespace

import pytest
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import RequestFactory

from auditoria.models import EventoAuditoria
from asociados.models import Asociado, CicloLectivo, Curso
from comercios.admin import ActividadComercialAdmin
from comercios.models import ActividadComercial, Comercio
from contenidos.models import CategoriaProductoServicio, ProductoServicio, Publicidad
from cuotas.admin import CuotaAdmin, DonacionAdmin, PagoAdmin, PagoCuotaAdmin
from cuotas.models import Cuota, Donacion, Pago, PagoCuota, PeriodoCuota
from usuarios.admin import Uni2UserAdmin


class DummyForm:
    def __init__(self, instance):
        self.instance = instance

    def save_m2m(self):
        return None


@pytest.mark.django_db
def test_admin_crud_simple_registra_alta_y_modificacion():
    actor = get_user_model().objects.create_superuser(
        username="admin_auditoria",
        password="secreto123",
        email="admin@example.com",
    )
    request = SimpleNamespace(user=actor)
    model_admin = ActividadComercialAdmin(ActividadComercial, admin.site)
    actividad = ActividadComercial(nombre="Gastronomía", descripcion="Descripción inicial")
    form = DummyForm(actividad)

    model_admin.save_model(request, actividad, form, change=False)
    model_admin.save_related(request, form, [], change=False)
    actividad.descripcion = "Descripción actualizada"
    model_admin.save_model(request, actividad, form, change=True)
    model_admin.save_related(request, form, [], change=True)

    eventos = EventoAuditoria.objects.filter(entidad="comercios.ActividadComercial").order_by("id")
    assert [evento.accion for evento in eventos] == [
        EventoAuditoria.ACCION_CREAR,
        EventoAuditoria.ACCION_MODIFICAR,
    ]
    assert eventos[1].cambios == {
        "descripcion": {
            "anterior": "Descripción inicial",
            "nuevo": "Descripción actualizada",
        }
    }
    assert all(evento.actor == actor for evento in eventos)
    assert all(evento.origen == EventoAuditoria.ORIGEN_ADMIN for evento in eventos)


@pytest.mark.django_db
def test_admin_usuario_registra_grupos_sin_guardar_password():
    actor = get_user_model().objects.create_superuser(
        username="admin_usuarios",
        password="secreto123",
        email="admin@example.com",
    )
    usuario = get_user_model().objects.create_user(username="operadora", password="clave-inicial")
    grupo = Group.objects.get(name="Atención al asociado")
    request = SimpleNamespace(user=actor)
    model_admin = Uni2UserAdmin(get_user_model(), admin.site)
    form = DummyForm(usuario)

    usuario.email = "operadora@example.com"
    model_admin.save_model(request, usuario, form, change=True)
    usuario.groups.add(grupo)
    model_admin.save_related(request, form, [], change=True)

    evento = EventoAuditoria.objects.get(entidad="auth.User", objeto_id=str(usuario.pk))
    assert set(evento.cambios) == {"email", "groups"}
    assert "password" not in evento.cambios
    assert "clave-inicial" not in str(evento.cambios)


@pytest.mark.parametrize(
    ("model_admin_class", "model"),
    [
        (CuotaAdmin, Cuota),
        (PagoAdmin, Pago),
        (PagoCuotaAdmin, PagoCuota),
        (DonacionAdmin, Donacion),
    ],
)
def test_admin_financiero_es_solo_lectura(model_admin_class, model):
    model_admin = model_admin_class(model, admin.site)
    request = SimpleNamespace(user=SimpleNamespace())

    assert model_admin.has_add_permission(request) is False
    assert model_admin.has_change_permission(request) is False
    assert model_admin.has_delete_permission(request) is False


def test_crud_simples_usados_por_el_admin_tienen_mixin_de_auditoria():
    modelos_auditados = (
        Asociado,
        CicloLectivo,
        Curso,
        PeriodoCuota,
        ActividadComercial,
        Comercio,
        CategoriaProductoServicio,
        ProductoServicio,
        Publicidad,
        get_user_model(),
        Group,
    )

    for model in modelos_auditados:
        assert hasattr(admin.site._registry[model], "audit_fields"), model._meta.label


@pytest.mark.django_db
@pytest.mark.parametrize("model", [Curso, Asociado, get_user_model()])
def test_admin_permite_borrar_datos_de_carga_inicial_solo_a_superusuario(model):
    superusuario = get_user_model().objects.create_superuser(
        username=f"root_{model._meta.model_name}",
        password="secreto123",
    )
    operador = get_user_model().objects.create_user(
        username=f"operador_{model._meta.model_name}",
        password="secreto123",
        is_staff=True,
    )
    model_admin = admin.site._registry[model]
    request_superusuario = RequestFactory().get("/admin/")
    request_superusuario.user = superusuario
    request_operador = RequestFactory().get("/admin/")
    request_operador.user = operador

    assert model_admin.has_delete_permission(request_superusuario) is True
    assert "delete_selected" in model_admin.get_actions(request_superusuario)
    assert model_admin.has_delete_permission(request_operador) is False
    assert "delete_selected" not in model_admin.get_actions(request_operador)


@pytest.mark.django_db
def test_admin_auditado_sin_habilitacion_mantiene_borrado_bloqueado():
    superusuario = get_user_model().objects.create_superuser(
        username="root_actividad",
        password="secreto123",
    )
    model_admin = admin.site._registry[ActividadComercial]

    assert model_admin.has_delete_permission(SimpleNamespace(user=superusuario)) is False
