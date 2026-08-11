---
type: "Caso de uso"
title: "CU-administrar-usuarios-accesos"
description: "Actor: Administrador de permisos."
tags: [mvp, caso-de-uso, usuarios, permisos]
timestamp: 2026-08-10T00:00:00-03:00
---

# CU-administrar-usuarios-accesos

**Actor:** usuario del grupo `Administrador de permisos`.

1. Entra al admin técnico y consulta usuarios.
2. Crea una cuenta o abre una cuenta no privilegiada existente.
3. Completa sus datos y asigna uno o más grupos según responsabilidades.
4. Guarda; el sistema alinea `is_staff` con la capacidad de acceso al admin.
5. Verifica la home y un acceso permitido con la cuenta de prueba.

**Resultado:** cuenta activa con privilegios acumulados y evento de auditoría.

**Restricciones:** puede consultar grupos, no modificar su matriz. No ve ni
edita superusuarios y no puede asignar `Administrador de la app`.

**Pruebas:** un grupo operativo; dos grupos acumulados; solo `Equipo del
proyecto`; retiro del último grupo con acceso al admin; intento sobre un
superusuario.
