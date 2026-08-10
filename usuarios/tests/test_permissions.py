import pytest
from django.contrib.auth.models import Group

from gestion.permissions import (
    GESTION_COBRAR_CUOTAS,
    GESTION_IMPORTAR_ASOCIADOS,
    GESTION_IMPORTAR_CUOTAS_HISTORICAS,
    GESTION_VER_AUDITORIA,
    GESTION_VER_MOVIMIENTOS_ASOCIADO,
)
from usuarios.roles import (
    ACCESO_ADMIN_TECNICO,
    ADMINISTRADOR_APP_GROUP,
    ADMINISTRADOR_MUTUAL_GROUP,
    ADMINISTRADOR_PERMISOS_GROUP,
    ATENCION_ASOCIADO_GROUP,
    DEFAULT_GROUPS,
    GESTION_CONVENIOS_GROUP,
    GESTION_PUBLICIDADES_GROUP,
)


def _tiene_permiso(grupo, permiso_natural):
    app_label, codename = permiso_natural.split(".", 1)
    return grupo.permissions.filter(
        content_type__app_label=app_label,
        codename=codename,
    ).exists()


@pytest.mark.django_db
def test_migracion_crea_todos_los_grupos_iniciales():
    assert set(DEFAULT_GROUPS).issubset(
        set(Group.objects.values_list("name", flat=True))
    )


@pytest.mark.django_db
def test_atencion_solo_recibe_permisos_de_operacion_diaria():
    grupo = Group.objects.get(name=ATENCION_ASOCIADO_GROUP)

    assert _tiene_permiso(grupo, GESTION_COBRAR_CUOTAS)
    assert _tiene_permiso(grupo, GESTION_VER_MOVIMIENTOS_ASOCIADO)
    assert not _tiene_permiso(grupo, GESTION_VER_AUDITORIA)
    assert not _tiene_permiso(grupo, GESTION_IMPORTAR_ASOCIADOS)


@pytest.mark.django_db
def test_grupos_de_dominio_reciben_solo_su_admin_tecnico():
    convenios = Group.objects.get(name=GESTION_CONVENIOS_GROUP)
    publicidades = Group.objects.get(name=GESTION_PUBLICIDADES_GROUP)

    assert _tiene_permiso(convenios, "comercios.change_comercio")
    assert _tiene_permiso(convenios, ACCESO_ADMIN_TECNICO)
    assert not _tiene_permiso(convenios, "contenidos.change_publicidad")
    assert _tiene_permiso(publicidades, "contenidos.change_publicidad")
    assert _tiene_permiso(publicidades, "comercios.view_comercio")
    assert not _tiene_permiso(publicidades, "comercios.change_comercio")


@pytest.mark.django_db
def test_administrador_permisos_gestiona_cuentas_sin_editar_grupos():
    grupo = Group.objects.get(name=ADMINISTRADOR_PERMISOS_GROUP)

    assert _tiene_permiso(grupo, "auth.change_user")
    assert _tiene_permiso(grupo, ACCESO_ADMIN_TECNICO)
    assert _tiene_permiso(grupo, "auth.view_group")
    assert not _tiene_permiso(grupo, "auth.change_group")
    assert _tiene_permiso(grupo, GESTION_VER_AUDITORIA)
    assert not _tiene_permiso(grupo, GESTION_VER_MOVIMIENTOS_ASOCIADO)


@pytest.mark.django_db
def test_administrador_mutual_no_recibe_importaciones_masivas():
    grupo = Group.objects.get(name=ADMINISTRADOR_MUTUAL_GROUP)

    assert _tiene_permiso(grupo, GESTION_VER_AUDITORIA)
    assert _tiene_permiso(grupo, GESTION_VER_MOVIMIENTOS_ASOCIADO)
    assert _tiene_permiso(grupo, "cuotas.view_pago")
    assert _tiene_permiso(grupo, "contenidos.change_publicidad")
    assert not _tiene_permiso(grupo, GESTION_IMPORTAR_ASOCIADOS)
    assert not _tiene_permiso(grupo, GESTION_IMPORTAR_CUOTAS_HISTORICAS)
    assert not _tiene_permiso(grupo, "auth.change_user")


@pytest.mark.django_db
def test_administrador_app_es_etiqueta_sin_permisos_de_grupo():
    grupo = Group.objects.get(name=ADMINISTRADOR_APP_GROUP)

    assert grupo.permissions.count() == 0
