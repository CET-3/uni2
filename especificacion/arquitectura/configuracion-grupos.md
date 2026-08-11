---
type: "Arquitectura"
title: "Configuración de grupos"
description: "Cómo se define, aplica y verifica la matriz de permisos de Uni2."
tags: [mvp, arquitectura, permisos, operacion]
timestamp: 2026-08-10T00:00:00-03:00
---

# Configuración de grupos

La fuente vigente es `usuarios/roles.py`: allí están los nombres y permisos
naturales (`app_label.codename`) de todos los grupos administrados por Uni2.
No se decide el acceso comparando nombres de grupos en las vistas.

`usuarios/group_configuration.py` compara y aplica esa definición. Al aplicar:

- crea los grupos faltantes;
- reemplaza los permisos de cada grupo por el conjunto exacto versionado;
- alinea `is_staff` con `usuarios.acceder_admin_tecnico`, incluido cualquier
  grupo futuro que reciba esa capacidad;
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
