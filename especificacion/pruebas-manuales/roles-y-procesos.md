---
type: "Prueba manual"
title: "Roles y procesos"
description: "Perfiles mínimos para capacitar y verificar la separación de responsabilidades."
tags: [mvp, prueba-manual, permisos, capacitacion]
timestamp: 2026-08-10T00:00:00-03:00
---

# Roles y procesos

## Preparación

1. Sincronizar la matriz con `python manage.py sincronizar_grupos --apply`.
2. Crear en staging una cuenta activa por cada fila y asignarle únicamente el
   grupo indicado.
3. Usar nombres reconocibles, por ejemplo `qa-atencion` o `qa-publicidades`.
4. No compartir contraseñas ni crear estas cuentas automáticamente en
   producción. Allí se asignan los grupos a personas reales autorizadas.

## Matriz de perfiles

| Perfil | Debe poder | Debe quedar denegado |
|---|---|---|
| Atención al asociado | Buscar, editar, cobrar y ver movimientos de ficha | Admin, auditoría general, períodos e importaciones |
| Administrador de permisos | Crear/editar usuarios, asignar grupos y ver auditoría | Cambiar grupos, superusuarios y operación económica |
| Gestión de convenios | Administrar actividades y comercios | Productos, publicidades, usuarios y auditoría |
| Gestión de productos y servicios | Administrar categorías y catálogo | Publicidades, comercios, usuarios y auditoría |
| Gestión de publicidades | Administrar publicidades y consultar objetos vinculables | Editar productos, comercios, usuarios y auditoría |
| Administrador de la mutual | Supervisar operación regular y auditoría | Importaciones masivas, permisos y superusuarios |
| Equipo del proyecto | Abrir Especificación y Design system | Admin y datos operativos |
| Asociados | Credencial, cuotas y beneficios de su vínculo | Gestión y admin |
| Comercios | Validar DNI o token desde su comercio | Gestión y admin |
| Administrador de la app | Operación técnica completa como superusuario | No se delega para una prueba funcional ordinaria |

## Casos comunes

Para cada perfil:

1. Iniciar sesión y registrar los accesos visibles en la home.
2. Completar un caso permitido del [mapa de procesos](../procesos/index.md).
3. Intentar abrir directamente una URL de la columna denegada.
4. Confirmar que no aparece el enlace y que la URL responde con denegación.
5. Cerrar sesión antes de cambiar de cuenta.

## Combinación de grupos

Crear una cuenta adicional con `Gestión de productos y servicios` y `Gestión de
publicidades`. Debe poder completar ambos procesos sin recibir permisos de
convenios, usuarios o auditoría. Esta prueba confirma que los grupos son
acumulables y evita inventar roles combinados.

## Evidencia sugerida

Registrar fecha, ambiente, versión, perfil, caso, resultado esperado, resultado
obtenido y captura sólo cuando aporte información. No incluir contraseñas,
tokens ni datos personales reales.
