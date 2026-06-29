# Usuarios Faltantes De Asociados Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Separar la importacion de asociados de la creacion masiva de usuarios y exponer esa creacion como boton en gestion.

**Architecture:** La importacion de padron queda limitada a `Asociado` y `Curso`. La creacion masiva de usuarios vive en `usuarios.services` como servicio idempotente y se invoca desde una vista POST de `gestion`.

**Tech Stack:** Django 5, templates Django, pytest, pytest-django.

---

### Task 1: Pruebas de comportamiento

**Files:**
- Modify: `gestion/tests/test_views.py`
- Modify: `usuarios/tests/test_services.py`

- [ ] Agregar prueba que confirme que importar padron no crea `User`.
- [ ] Agregar prueba de servicio para crear usuarios faltantes.
- [ ] Agregar prueba de vista POST que crea usuarios faltantes desde gestion.
- [ ] Ejecutar pruebas y verificar fallos esperados.

### Task 2: Separar importer y servicio de usuarios

**Files:**
- Modify: `asociados/importers.py`
- Modify: `usuarios/services.py`

- [ ] Quitar `create_user_for_asociado()` de `_upsert_asociado`.
- [ ] Crear resultado y funcion de servicio para asociados sin usuario.
- [ ] Mantener errores por asociado sin cortar el lote completo.

### Task 3: Exponer accion en gestion

**Files:**
- Modify: `gestion/views.py`
- Modify: `gestion/urls.py`
- Modify: `templates/gestion/importar_asociados.html`

- [ ] Agregar vista POST con permiso `gestion.importar_asociados`.
- [ ] Agregar URL `gestion/asociados/crear-usuarios-faltantes/`.
- [ ] Agregar boton con formulario POST junto a "Volver a asociados".

### Task 4: Documentacion y verificacion

**Files:**
- Modify: `especificacion/casos-de-uso/cu-importar-padron-inicial.md`
- Modify: `especificacion/casos-de-uso/cu-crear-usuario-asociado.md`
- Modify: `especificacion/reglas/usuarios.md`
- Modify: `especificacion/pantallas/gestion.md`

- [ ] Documentar que importar padron no crea usuarios.
- [ ] Documentar la accion masiva desde gestion.
- [ ] Ejecutar pruebas enfocadas.
- [ ] Revisar diff y estado de git.
