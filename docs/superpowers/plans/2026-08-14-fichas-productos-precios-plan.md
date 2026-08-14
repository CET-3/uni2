# Fichas de productos, destinatarios y precios Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Incorporar destinatarios escolares, imágenes y cuatro escenarios de precios a las fichas públicas de productos y servicios.

**Architecture:** `ProductoServicio` conserva sus dos campos de precio y deduce el escenario comercial a partir de sus valores. El admin toma combinaciones de ciclo y año de `Curso`, mientras un selector prepara bloques públicos por destinatario y escenario para que las vistas y templates solo compongan la respuesta.

**Tech Stack:** Django, Templates Django, Bootstrap 5, CSS, pytest y pytest-django.

## Global Constraints

- Mantener `User` estándar y la administración de contenidos en el admin técnico.
- Separar persistencia, consultas, HTTP y presentación entre `models.py`, `selectors.py`, `views.py` y templates.
- No agregar React, galerías, tablas de talles estructuradas ni precios por variantes.
- Conservar los cambios ajenos existentes en el árbol de trabajo.
- Actualizar los archivos OKF específicos en el mismo trabajo.
- Escribir nombres, ayudas, textos visibles y commits en castellano.

---

### Task 1: Modelo, validaciones y migración

**Files:**
- Create: `contenidos/tests/test_models.py`
- Modify: `contenidos/models.py`
- Modify: `usuarios/management/commands/carga_inicial.py`
- Create: `contenidos/migrations/0006_destinatarios_imagenes_y_precios_opcionales.py`

**Interfaces:**
- Produces: `ProductoServicio.tipo_precio`, con valores `diferenciado`, `unico`, `solo_asociados` o `sin_precio`.
- Produces: `ProductoServicio.ciclo_destinatario`, `curso_destinatario` y `foto`.
- Produces: `CategoriaProductoServicio.imagen_informativa` y `titulo_imagen_informativa`.

- [ ] **Step 1: Escribir pruebas fallidas de los cuatro escenarios y de las imágenes**

```python
@pytest.mark.parametrize(
    ("es_servicio", "asociados", "no_asociados", "esperado"),
    [
        (False, Decimal("100"), Decimal("150"), "diferenciado"),
        (False, Decimal("100"), Decimal("100"), "unico"),
        (False, Decimal("100"), None, "solo_asociados"),
        (True, None, None, "sin_precio"),
    ],
)
def test_producto_clasifica_tipo_precio(es_servicio, asociados, no_asociados, esperado):
    producto = ProductoServicio(
        es_servicio=es_servicio,
        precio_asociados=asociados,
        precio_no_asociados=no_asociados,
    )
    assert producto.tipo_precio == esperado

def test_producto_rechaza_curso_sin_ciclo(categoria):
    producto = ProductoServicio(
        categoria=categoria,
        nombre="Matemática",
        descripcion="Material",
        curso_destinatario="1ro",
        precio_asociados=100,
    )
    with pytest.raises(ValidationError):
        producto.full_clean()
```

Incluir funciones separadas llamadas
`test_producto_rechaza_precio_solo_para_no_asociados`,
`test_producto_rechaza_producto_sin_precio`,
`test_producto_rechaza_importes_cero`,
`test_producto_acepta_ciclo_sin_curso`,
`test_producto_acepta_ciclo_con_curso`,
`test_categoria_rechaza_imagen_sin_titulo` y
`test_categoria_rechaza_titulo_sin_imagen`; todas deben llamar `full_clean()`
y comprobar explícitamente éxito o `ValidationError` según su nombre.

- [ ] **Step 2: Ejecutar las pruebas y comprobar que fallan**

Run: `pytest contenidos/tests/test_models.py -q`

Expected: FAIL porque los campos, propiedades y validaciones todavía no existen.

- [ ] **Step 3: Implementar campos y validaciones mínimas**

En `ProductoServicio`, agregar constantes `PRECIO_DIFERENCIADO`, `PRECIO_UNICO`, `PRECIO_SOLO_ASOCIADOS`, `SIN_PRECIO`; los tres campos nuevos; precios con `blank=True, null=True`; `clean()` y la propiedad `tipo_precio`. En `CategoriaProductoServicio`, agregar los dos campos de imagen informativa y validar que se completen juntos.

```python
@property
def tipo_precio(self):
    if self.precio_asociados is None:
        return self.SIN_PRECIO
    if self.precio_no_asociados is None:
        return self.PRECIO_SOLO_ASOCIADOS
    if self.precio_asociados == self.precio_no_asociados:
        return self.PRECIO_UNICO
    return self.PRECIO_DIFERENCIADO
```

- [ ] **Step 4: Generar y revisar la migración**

Run: `python3 manage.py makemigrations contenidos`

Agregar una operación de datos que convierta a `NULL` ambos precios de servicios que actualmente tienen ambos valores en cero. Cambiar el dato inicial de `Préstamo de bicicleta` para usar `None`.

- [ ] **Step 5: Ejecutar pruebas de modelo y verificar migraciones**

Run: `pytest contenidos/tests/test_models.py -q`

Run: `python3 manage.py makemigrations --check`

Expected: todas las pruebas pasan y no quedan migraciones sin generar.

### Task 2: Opciones y trazabilidad en el admin

**Files:**
- Create: `contenidos/forms.py`
- Create: `contenidos/tests/test_admin.py`
- Modify: `contenidos/admin.py`

**Interfaces:**
- Consumes: campos y reglas de `ProductoServicio` de Task 1.
- Produces: `ProductoServicioAdminForm` con ciclos y años deduplicados desde cursos activos.

- [ ] **Step 1: Escribir pruebas fallidas del formulario**

```python
def test_formulario_deduplica_ciclo_y_anio_sin_turno_ni_comision(db, categoria):
    Curso.objects.create(anio="1ro", curso="1ra", division=Curso.DIVISION_CB, turno=Curso.TURNO_TM)
    Curso.objects.create(anio="1ro", curso="2da", division=Curso.DIVISION_CB, turno=Curso.TURNO_TT)

    form = ProductoServicioAdminForm()

    assert list(form.fields["curso_destinatario"].choices).count(("1ro", "1ro")) == 1
```

Incluir `test_formulario_acepta_combinacion_activa`,
`test_formulario_rechaza_combinacion_inexistente`,
`test_formulario_rechaza_curso_sin_ciclo` y
`test_formulario_conserva_combinacion_actual_inactiva`. Las tres primeras
construyen formularios ligados con los campos obligatorios completos; la última
crea el producto antes de desactivar su único `Curso` de origen y comprueba que
el formulario de edición siga siendo válido.

- [ ] **Step 2: Ejecutar las pruebas y comprobar que fallan**

Run: `pytest contenidos/tests/test_admin.py -q`

- [ ] **Step 3: Implementar el formulario y conectarlo a ambos admins**

`ProductoServicioAdminForm.__init__()` construye choices distintas desde `Curso.objects.filter(activo=True)`, añade los valores actuales y `clean()` valida la pareja seleccionada. Usar el formulario tanto en `ProductoServicioAdmin` como en `ProductoServicioInline`.

Agregar los nuevos campos a `fields`, `audit_fields`, `audit_inline_fields`, `list_display`, `list_filter` y `search_fields`. Los formateadores de precio deben devolver `—` para valores vacíos.

- [ ] **Step 4: Ejecutar pruebas del admin**

Run: `pytest contenidos/tests/test_admin.py contenidos/tests/test_models.py -q`

Expected: PASS.

### Task 3: Selector y composición pública

**Files:**
- Modify: `contenidos/selectors.py`
- Modify: `contenidos/tests/test_selectors.py`
- Modify: `web/views.py`

**Interfaces:**
- Consumes: `ProductoServicio.tipo_precio`.
- Produces: `get_bloques_productos_publicos(categoria) -> list[dict]`.
- Cada bloque expone `titulo` y `grupos_precio`; cada grupo expone `tipo_precio` e `items`.

- [ ] **Step 1: Escribir pruebas fallidas de agrupación y orden**

```python
def test_bloques_separan_generales_ciclo_completo_y_curso(categoria):
    crear_producto(categoria, nombre="General", orden=1)
    crear_producto(categoria, nombre="Todo CB", ciclo_destinatario="CB", orden=2)
    crear_producto(categoria, nombre="Primero", ciclo_destinatario="CB", curso_destinatario="1ro", orden=3)

    bloques = get_bloques_productos_publicos(categoria)

    assert [bloque["titulo"] for bloque in bloques] == ["Productos generales", "Ciclo Básico · Para todo el ciclo", "Ciclo Básico · 1ro"]
```

Cuando el único bloque de la categoría es el general, comprobar por separado
que su título sea `None` para conservar la tabla plana actual.

Incluir `test_bloques_excluyen_productos_inactivos`,
`test_bloques_respetan_orden_y_nombre` y
`test_bloques_separan_escenarios_contiguos_sin_reordenar`. La última crea la
secuencia diferenciado→único→diferenciado y comprueba tres grupos en ese mismo
orden.

- [ ] **Step 2: Ejecutar pruebas y comprobar que fallan**

Run: `pytest contenidos/tests/test_selectors.py -q`

- [ ] **Step 3: Implementar el selector y simplificar la vista**

Implementar `get_bloques_productos_publicos()` con una consulta ordenada y agrupación explícita. `CategoriaProductoServicioDetalleView.get_context_data()` agrega `bloques_productos`; su queryset conserva únicamente la carga de la categoría activa. La vista individual mantiene `select_related("categoria")`.

- [ ] **Step 4: Ejecutar pruebas de selector y vistas existentes**

Run: `pytest contenidos/tests/test_selectors.py web/tests/test_views.py -q`

Expected: selector nuevo y regresión pública pasan.

### Task 4: Templates públicos y estilos

**Files:**
- Modify: `templates/web/categoria_detalle.html`
- Modify: `templates/web/producto_servicio_detalle.html`
- Modify: `static/css/uni2-design-system.css`
- Modify: `web/tests/test_views.py`

**Interfaces:**
- Consumes: `bloques_productos`, `tipo_precio`, fotos e imagen informativa.
- Produces: filas enlazables, tablas con encabezados coherentes y ficha individual ampliada.

- [ ] **Step 1: Escribir pruebas fallidas para los cuatro casos visibles**

Crear una categoría con productos diferenciado, único, solo asociados y servicio sin precio. Verificar encabezados y textos:

```python
assert "Precio asociado" in contenido
assert "Precio no asociado" in contenido
assert "Solo asociados" in contenido
assert "Sin precio" in contenido
assert "$ 0,00" not in contenido
```

Verificar además enlace único por fila, miniatura opcional, foto grande, destinatario e imagen informativa titulada en ambas fichas.

- [ ] **Step 2: Ejecutar las pruebas y comprobar que fallan**

Run: `pytest web/tests/test_views.py -q`

- [ ] **Step 3: Implementar templates y CSS**

Renderizar una tabla por grupo de precio. Integrar la miniatura dentro de la celda del nombre para no reservar una columna vacía. Hacer que el enlace del nombre extienda su área interactiva sobre la fila con foco visible. En el detalle, omitir el panel numérico para servicios sin precio y mostrar el bloque de contacto.

Agregar clases `uni2-product-row`, `uni2-product-thumb`, `uni2-product-photo`, `uni2-informative-image`, `uni2-price-badge` y sus ajustes mobile/dark theme usando las variables existentes.

- [ ] **Step 4: Ejecutar las pruebas públicas**

Run: `pytest web/tests/test_views.py contenidos/tests/test_selectors.py -q`

Expected: PASS.

### Task 5: Especificación y verificación integral

**Files:**
- Modify: `especificacion/entidades/producto-servicio.md`
- Modify: `especificacion/entidades/categoria-producto-servicio.md`
- Modify: `especificacion/reglas/productos-servicios.md`
- Modify: `especificacion/casos-de-uso/cu-listar-productos-servicios-publicos.md`
- Modify: `especificacion/casos-de-uso/cu-administrar-productos-servicios.md`
- Modify: `especificacion/pantallas/sitio-publico.md`
- Modify: `especificacion/arquitectura/media.md`

**Interfaces:**
- Consumes: comportamiento final verificado en Tasks 1–4.
- Produces: trazabilidad OKF completa del cambio.

- [ ] **Step 1: Actualizar entidad, reglas, casos de uso, pantalla y media**

Documentar nombres exactos, opcionalidad, cuatro escenarios de precios, regla curso→ciclo, origen de combinaciones desde `Curso`, administración técnica, agrupación, imágenes y navegación de la fila a la ficha.

- [ ] **Step 2: Revisar consistencia de índices y referencias**

No se crean archivos OKF nuevos, por lo que no deben modificarse índices de directorio. Comprobar que todas las referencias apunten a archivos existentes.

- [ ] **Step 3: Ejecutar verificaciones focalizadas e integrales**

Run: `pytest contenidos/tests web/tests/test_views.py -q`

Run: `pytest -q`

Run: `python3 manage.py makemigrations --check`

Run: `python3 manage.py check`

Expected: todas las órdenes terminan con código 0.

- [ ] **Step 4: Revisar diff y estado final**

Run: `git diff --check`

Run: `git status --short`

Confirmar que el cambio previo ajeno en `especificacion/pantallas/sitio-publico.md` siga presente y no atribuirlo a esta implementación.
