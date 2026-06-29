import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.urls import reverse
from pytest_django.asserts import assertContains, assertNotContains

from asociados.services import create_asociado
from comercios.models import ActividadComercial, Comercio
from gestion.permissions import GESTION_COBRAR_CUOTAS, GESTION_VER_DESIGN_SYSTEM, GESTION_VER_ESPECIFICACION
from usuarios.services import COMERCIO_GROUP


@pytest.mark.django_db
def test_login_redirige_a_panel_asociado(client):
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
    assert response.url == reverse("asociados:dashboard")


@pytest.mark.django_db
def test_login_redirige_a_panel_comercio(client):
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
    assert response.url == reverse("comercios:dashboard")


@pytest.mark.django_db
def test_login_usuario_con_grupo_comercio_sin_perfil_redirige_a_home(client):
    group = Group.objects.get_or_create(name=COMERCIO_GROUP)[0]
    user_model = get_user_model()
    user = user_model.objects.create_user(username="com_sin_perfil", password="secreto123")
    user.groups.add(group)

    response = client.post(
        reverse("usuarios:login"),
        {"username": "com_sin_perfil", "password": "secreto123"},
    )

    assert response.status_code == 302
    assert response.url == reverse("web:home")


@pytest.mark.django_db
def test_login_usuario_con_permiso_redirige_a_dashboard_de_gestion(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(
        username="admin_gestion",
        password="secreto123",
    )
    permiso = Permission.objects.get(content_type__app_label="gestion", codename="cobrar_cuotas")
    user.user_permissions.add(permiso)

    response = client.post(
        reverse("usuarios:login"),
        {"username": "admin_gestion", "password": "secreto123"},
    )

    assert response.status_code == 302
    assert response.url == reverse("gestion:dashboard")


@pytest.mark.django_db
def test_login_con_asociado_y_permiso_gestion_redirige_a_selector(client):
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
    assert response.url == reverse("usuarios:selector_panel")


@pytest.mark.django_db
def test_smart_start_muestra_home_publica_sin_sesion(client):
    response = client.get(reverse("web:home"))
    assert response.status_code == 200
    assert "UNI2" in response.content.decode()


@pytest.mark.django_db
def test_smart_start_redirige_a_asociado_con_esa_experiencia(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="aso_smart", password="secreto123")
    asociado = create_asociado(nombre="S", apellido="Mart", dni="46111999", tipo="asociado", fecha_alta="2026-06-01")
    asociado.usuario = user
    asociado.save(update_fields=["usuario"])

    client.force_login(user)
    response = client.get(reverse("web:home"))

    assert response.status_code == 302
    assert response.url == reverse("asociados:dashboard")


@pytest.mark.django_db
def test_smart_start_redirige_a_gestion_con_esa_experiencia(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="gest_smart", password="secreto123")
    permiso = Permission.objects.get(content_type__app_label="gestion", codename="ver_dashboard_gestion")
    user.user_permissions.add(permiso)

    client.force_login(user)
    response = client.get(reverse("web:home"))

    assert response.status_code == 302
    assert response.url == reverse("gestion:dashboard")


@pytest.mark.django_db
def test_smart_start_redirige_a_comercio_con_esa_experiencia(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="com_smart", password="secreto123")
    actividad = ActividadComercial.objects.create(nombre="Libros")
    Comercio.objects.create(nombre="Libreria", direccion="Av 1", actividad_comercial=actividad, usuario=user)

    client.force_login(user)
    response = client.get(reverse("web:home"))

    assert response.status_code == 302
    assert response.url == reverse("comercios:dashboard")


@pytest.mark.django_db
def test_smart_start_redirige_a_selector_con_dos_experiencias(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="multi_smart", password="secreto123")
    asociado = create_asociado(nombre="M", apellido="Ulti", dni="47111999", tipo="asociado", fecha_alta="2026-06-01")
    asociado.usuario = user
    asociado.save(update_fields=["usuario"])
    permiso = Permission.objects.get(content_type__app_label="gestion", codename="cobrar_cuotas")
    user.user_permissions.add(permiso)

    client.force_login(user)
    response = client.get(reverse("web:home"))

    assert response.status_code == 302
    assert response.url == reverse("usuarios:selector_panel")


@pytest.mark.django_db
def test_smart_start_muestra_home_publica_sin_experiencias(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="sin_exp", password="secreto123")

    client.force_login(user)
    response = client.get(reverse("web:home"))

    assert response.status_code == 200


@pytest.mark.django_db
def test_selector_panel_muestra_experiencias_disponibles(client):
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
    permiso = Permission.objects.get(content_type__app_label="gestion", codename="cobrar_cuotas")
    user.user_permissions.add(permiso)

    client.force_login(user)
    response = client.get(reverse("usuarios:selector_panel"))

    assert response.status_code == 200
    content = response.content.decode()
    assert "Mi cuenta de asociado" in content
    assert "Gestión" in content


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
    response = client.get(reverse("web:inicio"))

    assert response.status_code == 200
    content = response.content.decode()
    assert "Ana Perez" in content
    assert "dropdown-menu" in content
    assert "Mi panel" in content
    assert "Cambiar panel" not in content


@pytest.mark.django_db
def test_navbar_muestra_cambiar_panel_si_hay_mas_de_una_experiencia(client):
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
    permiso = Permission.objects.get(content_type__app_label="gestion", codename="cobrar_cuotas")
    user.user_permissions.add(permiso)

    client.force_login(user)
    response = client.get(reverse("web:inicio"))

    assert response.status_code == 200
    content = response.content.decode()
    assert "Atención Mutual" in content
    assert "dropdown-menu" in content
    assert "Mi panel" in content
    assert "Panel de gestión" in content
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
    response = client.get(reverse("web:inicio"))

    assert response.status_code == 200
    content = response.content.decode()
    assert reverse("web:design-system") in content
    assert "Design system" in content
    assert "uni2-user-menu-link" in content


@pytest.mark.django_db
def test_navbar_agrupa_herramientas_internas_para_staff(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(
        username="admin_nav",
        password="secreto123",
        is_staff=True,
    )
    permisos = Permission.objects.filter(
        content_type__app_label="gestion",
        codename__in=[
            GESTION_VER_ESPECIFICACION.split(".", 1)[1],
            GESTION_VER_DESIGN_SYSTEM.split(".", 1)[1],
        ],
    )
    user.user_permissions.add(*permisos)

    client.force_login(user)
    response = client.get(reverse("web:inicio"))

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
def test_navbar_no_muestra_design_system_sin_permiso(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="sin_doc_visual", password="secreto123")

    client.force_login(user)
    response = client.get(reverse("web:home"))

    assert response.status_code == 200
    assertNotContains(response, reverse("web:design-system"))
    assertNotContains(response, "Design system")
