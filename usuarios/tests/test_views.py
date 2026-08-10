import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.urls import reverse
from pytest_django.asserts import assertContains, assertNotContains

from asociados.services import create_asociado
from comercios.models import ActividadComercial, Comercio
from gestion.permissions import (
    GESTION_COBRAR_CUOTAS,
    GESTION_VER_DESIGN_SYSTEM,
    GESTION_VER_DEUDORES,
    GESTION_VER_ESPECIFICACION,
)
from usuarios.home_navigation import build_home_navigation
from usuarios.roles import ACCESO_ADMIN_TECNICO, EQUIPO_PROYECTO_GROUP
from usuarios.services import COMERCIO_GROUP


@pytest.mark.django_db
def test_login_redirige_a_home_con_variante_asociado(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="aso", password="secreto123")
    asociado = create_asociado(
        nombre="Ana",
        apellido="Perez",
        dni="40111999",
        tipo="asociado",
        fecha_alta="2026-05-10",
    )
    asociado.usuario = user
    asociado.save(update_fields=["usuario"])

    response = client.post(
        reverse("usuarios:login"),
        {"username": "aso", "password": "secreto123"},
    )

    assert response.status_code == 302
    assert response.url == reverse("web:home")


def test_login_presenta_controles_claros_y_autocompletables(client):
    response = client.get(reverse("usuarios:login"))
    content = response.content.decode()

    assert 'class="form-control"' in content
    assert 'autocomplete="username"' in content
    assert 'autocomplete="current-password"' in content
    assert "Ingresar a Uni2" in content


@pytest.mark.django_db
def test_login_redirige_a_home_con_variante_comercio(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="com", password="secreto123")
    actividad = ActividadComercial.objects.create(nombre="Libreria")
    Comercio.objects.create(
        nombre="Libreria Sur",
        direccion="Mitre 123",
        actividad_comercial=actividad,
        beneficio_texto="10% en utiles",
        usuario=user,
    )

    response = client.post(
        reverse("usuarios:login"),
        {"username": "com", "password": "secreto123"},
    )

    assert response.status_code == 302
    assert response.url == reverse("web:home")


@pytest.mark.django_db
def test_login_usuario_con_grupo_comercio_sin_perfil_redirige_a_home(client):
    group = Group.objects.get_or_create(name=COMERCIO_GROUP)[0]
    user_model = get_user_model()
    user = user_model.objects.create_user(
        username="com_sin_perfil", password="secreto123"
    )
    user.groups.add(group)

    response = client.post(
        reverse("usuarios:login"),
        {"username": "com_sin_perfil", "password": "secreto123"},
    )

    assert response.status_code == 302
    assert response.url == reverse("web:home")


@pytest.mark.django_db
def test_login_usuario_con_permiso_redirige_a_home(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(
        username="admin_gestion",
        password="secreto123",
    )
    permiso = Permission.objects.get(
        content_type__app_label="gestion", codename="cobrar_cuotas"
    )
    user.user_permissions.add(permiso)

    response = client.post(
        reverse("usuarios:login"),
        {"username": "admin_gestion", "password": "secreto123"},
    )

    assert response.status_code == 302
    assert response.url == reverse("web:home")


@pytest.mark.django_db
def test_login_con_asociado_y_permiso_gestion_redirige_a_home(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="aso_gestion", password="secreto123")
    asociado = create_asociado(
        nombre="Lia",
        apellido="Perez",
        dni="41111999",
        tipo="asociado",
        fecha_alta="2026-05-10",
    )
    asociado.usuario = user
    asociado.save(update_fields=["usuario"])
    permiso = Permission.objects.get(
        content_type__app_label="gestion",
        codename=GESTION_COBRAR_CUOTAS.split(".", 1)[1],
    )
    user.user_permissions.add(permiso)

    response = client.post(
        reverse("usuarios:login"),
        {"username": "aso_gestion", "password": "secreto123"},
    )

    assert response.status_code == 302
    assert response.url == reverse("web:home")


@pytest.mark.django_db
def test_home_muestra_variante_publica_sin_sesion(client):
    response = client.get(reverse("web:home"))
    assert response.status_code == 200
    assert "UNI2" in response.content.decode()


@pytest.mark.django_db
def test_home_muestra_variante_asociado_con_esa_experiencia(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="aso_smart", password="secreto123")
    asociado = create_asociado(
        nombre="S",
        apellido="Mart",
        dni="46111999",
        tipo="asociado",
        fecha_alta="2026-06-01",
    )
    asociado.usuario = user
    asociado.save(update_fields=["usuario"])

    client.force_login(user)
    response = client.get(reverse("web:home"))

    assert response.status_code == 200
    content = response.content.decode()
    assert "Hola, S." in content
    assert "Mi credencial" in content
    assert "Mis cuotas" in content
    assert "Cómo ser parte de nuestra comunidad" in content


@pytest.mark.django_db
def test_home_muestra_variante_gestion_con_esa_experiencia(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="gest_smart", password="secreto123")
    permiso = Permission.objects.get(
        content_type__app_label="gestion", codename="ver_dashboard_gestion"
    )
    user.user_permissions.add(permiso)

    client.force_login(user)
    response = client.get(reverse("web:home"))

    assert response.status_code == 200
    content = response.content.decode()
    assert "Panel de gestión" in content
    assert "Cómo ser parte de nuestra comunidad" in content


@pytest.mark.django_db
def test_home_muestra_variante_comercio_con_esa_experiencia(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="com_smart", password="secreto123")
    actividad = ActividadComercial.objects.create(nombre="Libros")
    Comercio.objects.create(
        nombre="Libreria", direccion="Av 1", actividad_comercial=actividad, usuario=user
    )

    client.force_login(user)
    response = client.get(reverse("web:home"))

    assert response.status_code == 200
    content = response.content.decode()
    assert "Libreria" in content
    assert "Validar credencial" in content
    assert "Cómo ser parte de nuestra comunidad" in content


@pytest.mark.django_db
def test_home_muestra_selector_con_dos_experiencias(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="multi_smart", password="secreto123")
    asociado = create_asociado(
        nombre="M",
        apellido="Ulti",
        dni="47111999",
        tipo="asociado",
        fecha_alta="2026-06-01",
    )
    asociado.usuario = user
    asociado.save(update_fields=["usuario"])
    permiso = Permission.objects.get(
        content_type__app_label="gestion", codename="cobrar_cuotas"
    )
    user.user_permissions.add(permiso)

    client.force_login(user)
    response = client.get(reverse("web:home"))

    assert response.status_code == 200
    content = response.content.decode()
    assert "Elegí cómo querés ingresar" in content
    assert "Hola" not in content
    assert "Mi cuenta de asociado" in content
    assert "Administración" in content


@pytest.mark.django_db
def test_home_muestra_variante_publica_sin_experiencias(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="sin_exp", password="secreto123")

    client.force_login(user)
    response = client.get(reverse("web:home"))

    assert response.status_code == 200


@pytest.mark.django_db
def test_home_permite_elegir_una_experiencia_disponible(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="selector", password="secreto123")
    asociado = create_asociado(
        nombre="Noa",
        apellido="Rios",
        dni="42111999",
        tipo="asociado",
        fecha_alta="2026-05-10",
    )
    asociado.usuario = user
    asociado.save(update_fields=["usuario"])
    permiso = Permission.objects.get(
        content_type__app_label="gestion", codename="cobrar_cuotas"
    )
    user.user_permissions.add(permiso)

    client.force_login(user)
    response = client.get(reverse("web:home"), {"perfil": "asociado"})

    assert response.status_code == 200
    content = response.content.decode()
    assert "Hola, Noa." in content
    assert "Mi credencial" in content
    assert "Elegí cómo querés ingresar" not in content


@pytest.mark.django_db
def test_home_multiperfil_limita_el_hero_a_dos_cta_y_muestra_el_tercero_debajo(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(
        username="tres_perfiles", password="secreto123"
    )
    asociado = create_asociado(
        nombre="Tres",
        apellido="Perfiles",
        dni="42111998",
        tipo="asociado",
        fecha_alta="2026-05-10",
    )
    asociado.usuario = user
    asociado.save(update_fields=["usuario"])
    actividad = ActividadComercial.objects.create(nombre="Servicios")
    Comercio.objects.create(
        nombre="Comercio múltiple",
        actividad_comercial=actividad,
        usuario=user,
    )
    permiso = Permission.objects.get(
        content_type__app_label="gestion", codename="ver_dashboard_gestion"
    )
    user.user_permissions.add(permiso)

    client.force_login(user)
    response = client.get(reverse("web:home"))

    navigation = response.context["home_navigation"]
    assert response.status_code == 200
    assert navigation["variant"] == "multiperfil"
    assert [action.label for action in navigation["primary_actions"]] == [
        "Mi cuenta de asociado",
        "Mi comercio",
    ]
    assert [action.label for action in navigation["extra_actions"]] == [
        "Administración"
    ]
    assert "Más accesos" in response.content.decode()


@pytest.mark.django_db
def test_home_multiperfil_rechaza_un_perfil_no_disponible(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(
        username="perfil_invalido", password="secreto123"
    )
    asociado = create_asociado(
        nombre="Perfil",
        apellido="Inválido",
        dni="42111997",
        tipo="asociado",
        fecha_alta="2026-05-10",
    )
    asociado.usuario = user
    asociado.save(update_fields=["usuario"])
    permiso = Permission.objects.get(
        content_type__app_label="gestion", codename="ver_dashboard_gestion"
    )
    user.user_permissions.add(permiso)

    client.force_login(user)
    response = client.get(reverse("web:home"), {"perfil": "comercio"})

    assert response.context["home_navigation"]["variant"] == "multiperfil"
    assert "Elegí cómo querés ingresar" in response.content.decode()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "path",
    ["/inicio/", "/paneles/", "/comercio/panel/"],
)
def test_rutas_anteriores_de_inicio_y_paneles_fueron_retiradas(client, path):
    assert client.get(path).status_code == 404


@pytest.mark.django_db
def test_navbar_muestra_nombre_y_panel_unico(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(
        username="ana",
        password="secreto123",
        first_name="Ana",
        last_name="Perez",
    )
    asociado = create_asociado(
        nombre="Ana",
        apellido="Perez",
        dni="43111999",
        tipo="asociado",
        fecha_alta="2026-05-10",
    )
    asociado.usuario = user
    asociado.save(update_fields=["usuario"])

    client.force_login(user)
    response = client.get(reverse("web:home"))

    assert response.status_code == 200
    content = response.content.decode()
    assert "Ana Perez" in content
    assert "dropdown-menu" in content
    assert "Mi cuenta de asociado" in content
    assert "Cambiar panel" not in content


@pytest.mark.django_db
def test_navbar_muestra_todas_las_experiencias_disponibles(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(
        username="atencion_nav",
        password="secreto123",
        first_name="Atención",
        last_name="Mutual",
    )
    asociado = create_asociado(
        nombre="Atención",
        apellido="Mutual",
        dni="44111999",
        tipo="asociado",
        fecha_alta="2026-05-10",
    )
    asociado.usuario = user
    asociado.save(update_fields=["usuario"])
    permiso = Permission.objects.get(
        content_type__app_label="gestion", codename="cobrar_cuotas"
    )
    user.user_permissions.add(permiso)

    client.force_login(user)
    response = client.get(reverse("web:home"))

    assert response.status_code == 200
    content = response.content.decode()
    assert "Atención Mutual" in content
    assert "dropdown-menu" in content
    assert "Mi cuenta de asociado" in content
    assert "Administración" in content
    assert "Cambiar panel" not in content


@pytest.mark.django_db
def test_navbar_muestra_design_system_si_tiene_permiso(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="doc_visual", password="secreto123")
    permiso = Permission.objects.get(
        content_type__app_label="gestion",
        codename=GESTION_VER_DESIGN_SYSTEM.split(".", 1)[1],
    )
    user.user_permissions.add(permiso)

    client.force_login(user)
    response = client.get(reverse("web:home"))

    assert response.status_code == 200
    content = response.content.decode()
    assert reverse("web:design-system") in content
    assert "Design system" in content
    assert "uni2-user-menu-link" in content


@pytest.mark.django_db
def test_navbar_agrupa_herramientas_internas_para_capacidad_admin(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(
        username="admin_nav",
        password="secreto123",
        is_staff=True,
    )
    permisos = [
        Permission.objects.get(
            content_type__app_label=app_label,
            codename=codename,
        )
        for app_label, codename in (
            GESTION_VER_ESPECIFICACION.split(".", 1),
            GESTION_VER_DESIGN_SYSTEM.split(".", 1),
            ACCESO_ADMIN_TECNICO.split(".", 1),
        )
    ]
    user.user_permissions.add(*permisos)

    client.force_login(user)
    response = client.get(reverse("web:home"))

    assert response.status_code == 200
    content = response.content.decode()
    assert 'class="dropdown-menu dropdown-menu-end uni2-user-menu"' in content
    assert "Herramientas" in content
    assert "Admin técnico" in content
    assert "Especificación" in content
    assert "Design system" in content
    assert "uni2-user-menu-section" in content
    assert "uni2-user-menu-link" in content


@pytest.mark.django_db
def test_is_staff_sin_capacidad_no_muestra_admin_tecnico(client):
    user = get_user_model().objects.create_user(
        username="staff_sin_capacidad",
        is_staff=True,
    )
    client.force_login(user)

    response = client.get(reverse("web:home"))

    assert response.status_code == 200
    assertNotContains(response, "Admin técnico")
    assertNotContains(response, reverse("admin:index"))


@pytest.mark.django_db
def test_equipo_proyecto_ve_documentacion_pero_no_admin_tecnico(client):
    user = get_user_model().objects.create_user(username="equipo-proyecto")
    user.groups.add(Group.objects.get(name=EQUIPO_PROYECTO_GROUP))
    client.force_login(user)

    response = client.get(reverse("web:home") + "?perfil=gestion")

    assertContains(response, "Especificación")
    assertContains(response, "Design system")
    assertNotContains(response, "Admin técnico")
    assert client.get(reverse("admin:index")).status_code == 302


@pytest.mark.django_db
def test_superusuario_muestra_admin_tecnico(client):
    user = get_user_model().objects.create_superuser(
        username="superusuario_nav",
        password="secreto123",
    )
    client.force_login(user)

    response = client.get(reverse("web:home"))

    assertContains(response, "Admin técnico")
    assertContains(response, reverse("admin:index"))


@pytest.mark.django_db
def test_home_no_ofrece_ver_deudores_aunque_el_usuario_tenga_permiso():
    user = get_user_model().objects.create_user(username="reporte_deudores")
    app_label, codename = GESTION_VER_DEUDORES.split(".", 1)
    user.user_permissions.add(
        Permission.objects.get(
            content_type__app_label=app_label,
            codename=codename,
        )
    )

    navigation = build_home_navigation(user, requested_profile="gestion")
    actions = navigation["primary_actions"] + navigation["extra_actions"]

    assert "Ver deudores" not in [action.label for action in actions]
    assert reverse("gestion:deudores") not in [action.url for action in actions]


@pytest.mark.django_db
def test_navbar_no_muestra_design_system_sin_permiso(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(
        username="sin_doc_visual", password="secreto123"
    )

    client.force_login(user)
    response = client.get(reverse("web:home"))

    assert response.status_code == 200
    assertNotContains(response, reverse("web:design-system"))
    assertNotContains(response, "Design system")
