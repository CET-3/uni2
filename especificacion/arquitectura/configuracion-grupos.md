---
type: "Arquitectura"
title: "Configuración de grupos"
description: "Cómo se define, aplica y verifica la matriz de permisos de Uni2."
tags: [mvp, arquitectura, permisos, operacion]
timestamp: 2026-08-10T00:00:00-03:00
---

# Configuración de grupos

Los grupos y sus permisos pueden ser definidos por cada mutual desde el admin.
Uni2 no necesita conocer ni versionar los nombres de esos grupos. Los permisos
se expresan con sus claves naturales (`app_label.codename`) y las vistas o el
admin consultan las capacidades efectivas del usuario, no el nombre de su
grupo.

`usuarios/group_configuration.py` compara y aplica esa definición. Al aplicar:

- crea los grupos faltantes;
- reemplaza los permisos de cada grupo por el conjunto exacto versionado;
- conserva la sincronización histórica de `is_staff` para compatibilidad;
- conserva `is_staff` en superusuarios;
- no agrega ni elimina integrantes de los grupos.

## Comando operativo

```bash
python manage.py sincronizar_grupos
python manage.py sincronizar_grupos --apply
python manage.py sincronizar_grupos --check
```

El primer comando informa sin escribir. `--apply` corrige y puede repetirse sin
efectos adicionales. `--check` termina con error si hay diferencias y sirve
como control automatizado.

La migración `usuarios.0006_reorganizar_grupos_operativos` aplica la matriz al
actualizar un ambiente. Como el grupo histórico `Gestión de publicidades`
incluía también el catálogo, copia sus integrantes a `Gestión de productos y
servicios` antes de separar permisos. Luego el responsable de accesos puede
retirar el grupo que no corresponda a cada persona.

`carga_inicial` reutiliza el mismo servicio; no mantiene una segunda matriz.
Los cambios futuros deben modificar la definición, agregar una migración de
datos, actualizar pruebas y actualizar la especificación en el mismo trabajo.

## Acceso al admin técnico

Una cuenta activa puede entrar al admin técnico si es superusuario o si tiene
al menos un permiso efectivo (`view`, `add`, `change` o `delete`) sobre un
modelo registrado en el admin. `is_staff` no es la fuente funcional de esta
autorización. Dentro del admin, cada `ModelAdmin` continúa aplicando sus
propias restricciones.
