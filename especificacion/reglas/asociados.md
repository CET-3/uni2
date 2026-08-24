---
type: "Regla de negocio"
title: "Asociados"
description: "Reglas de negocio sobre asociados."
tags: [mvp, reglas]
timestamp: 2026-06-22T00:00:00-03:00
---

# Asociados

1. Un asociado puede ser de tipo asociado o adherente.
2. Si el tipo es asociado, debe tener un curso cargado y no una clasificación de adherente. Si el tipo es adherente, debe tener una clasificación y no debe tener curso.
3. Al cambiar el tipo se limpia automáticamente el dato anterior y se exige el nuevo. Tipo, curso y clasificación se registran juntos en auditoría.
4. Los asociados participan de asambleas; los adherentes no.
5. Los asociados inactivos conservan sus datos, cuotas y pagos.
6. Solo los asociados activos generan nuevas cuotas.
7. No puede existir más de un asociado con el mismo DNI.
8. El número de asociado debe generarse automáticamente.
9. Un asociado puede existir sin usuario de acceso.
10. Al crear un asociado se puede crear también un usuario de acceso vinculado.
11. La edición ordinaria no muestra ni acepta `estado`, `fecha_baja` o
    `motivo_baja`. Mientras no exista el caso de uso específico de baja, esos
    campos quedan visibles únicamente para el superusuario técnico en el admin.
12. Durante la depuración excepcional de la carga inicial, un superusuario
    puede eliminar físicamente asociados y cursos desde el admin técnico. La
    confirmación de Django informa los objetos relacionados: al eliminar un
    asociado también se eliminan sus cuotas, pagos, aplicaciones de pagos y
    donaciones; al eliminar un curso, los asociados que lo usaban quedan sin
    curso actual. La baja lógica continúa siendo el flujo ordinario fuera de
    esta limpieza inicial.
