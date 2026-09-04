# Método efectivo por defecto en cuotas históricas Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Hacer que un pago histórico marcado como realizado y sin forma informada se previsualice y persista como efectivo.

**Architecture:** La normalización se corregirá en `analyze_cuotas_historicas_xlsx()` antes de construir el diccionario de previsualización. El importador consumirá ese valor sin agregar una segunda regla divergente.

**Tech Stack:** Python, Django, openpyxl, pytest, pytest-django.

## Global Constraints

- El cambio se limita al método por defecto de pagos realizados con forma vacía.
- Una forma no vacía y dudosa continúa en revisión.
- No se modifica la búsqueda de asociados, importes, períodos ni estados.
- La especificación OKF se actualiza junto con el código.

---

### Task 1: Normalizar efectivo antes de construir la previsualización

**Files:**
- Modify: `cuotas/importers.py`
- Modify: `gestion/tests/test_views.py`
- Modify: `especificacion/casos-de-uso/cu-importar-cuotas-historicas.md`

**Interfaces:**
- Consumes: `_normalize_bool(value) -> tuple[bool, str]` y `_normalize_metodo(value) -> tuple[str, str]`.
- Produces: cada item importable con `pagada=True` y forma vacía contiene `metodo=Pago.METODO_EFECTIVO`.

- [ ] **Step 1: Escribir la prueba de integración fallida**

Agregar un test que cree un asociado y una planilla con marzo marcado `True` y
forma vacía. Después de previsualizar debe comprobar:

```python
preview = client.session["cuotas_historicas_preview"]
marzo = next(item for item in preview["importables"] if item["mes"] == 3)
assert marzo["pagada"] is True
assert marzo["metodo"] == Pago.METODO_EFECTIVO
```

Luego debe confirmar la importación y comprobar el dato persistido:

```python
pago = Pago.objects.get(asociado=asociado, fecha=date(2026, 3, 10))
assert pago.metodo == Pago.METODO_EFECTIVO
```

- [ ] **Step 2: Ejecutar la prueba y comprobar el fallo correcto**

Run: `pytest gestion/tests/test_views.py::test_importar_cuota_historica_pagada_sin_forma_asume_efectivo -q`

Expected: FAIL porque `marzo["metodo"]` es una cadena vacía.

- [ ] **Step 3: Implementar el cambio mínimo**

Mover la regla existente antes de construir `item`:

```python
pagada, pago_note = _normalize_bool(raw_pagada)
metodo, metodo_note = _normalize_metodo(raw_forma)
if not pagada and metodo:
    pagada = True
if pagada and not metodo and not metodo_note:
    metodo = Pago.METODO_EFECTIVO
```

Eliminar la asignación tardía que actualmente ocurre después de crear el
diccionario. La condición `not metodo_note` evita convertir formas no vacías y
dudosas en efectivo.

- [ ] **Step 4: Ejecutar la prueba focalizada**

Run: `pytest gestion/tests/test_views.py::test_importar_cuota_historica_pagada_sin_forma_asume_efectivo -q`

Expected: PASS.

- [ ] **Step 5: Actualizar la especificación**

En `cu-importar-cuotas-historicas.md`, aclarar que un pago realizado con forma
vacía se presume efectivo y que solamente una forma no vacía pero desconocida
queda para revisar.

- [ ] **Step 6: Ejecutar verificación completa**

Run: `pytest cuotas/tests/test_importers.py gestion/tests/test_views.py -q`

Expected: PASS.

Run: `git diff --check`

Expected: sin errores.

Run: `pytest -q`

Expected: PASS.

- [ ] **Step 7: Confirmar el cambio**

```bash
git add cuotas/importers.py gestion/tests/test_views.py especificacion/casos-de-uso/cu-importar-cuotas-historicas.md
git commit -m "Asume efectivo en pagos historicos sin forma"
```
