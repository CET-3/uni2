---
type: "Caso de uso"
title: "CU-refrescar-staging"
description: "Crear una copia aislada y endurecida de los datos productivos para validación."
tags: [mvp, staging, operacion, seguridad]
timestamp: 2026-08-02T00:00:00-03:00
---

# CU-refrescar-staging

**Actor:** Responsable técnica autorizada.

### Precondiciones

- Existe una base staging nueva, vacía y desconectada.
- El acceso a Producción es temporal y de sólo lectura.
- Origen y destino tienen identidades y credenciales diferentes.
- Se definió un refresh ID nuevo.

### Flujo principal

1. La responsable registra el motivo y el identificador del refresco.
2. Transmite una copia consistente de Producción al destino sin owners ni
   privilegios y sin dejar un dump sin cifrar.
3. Revisa y aplica las migraciones compatibles sobre la base desconectada.
4. Ejecuta `preparar_copia_staging` confirmando el destino.
5. El sistema elimina sesiones, invalida usuarios copiados y regenera tokens.
6. El sistema crea un admin, dos asociados ficticios y un comercio ficticio,
   cada uno con una cuenta QA y un secreto exclusivo.
7. Como último paso transaccional, el sistema escribe el marcador del refresh.
8. La responsable verifica conteos, readiness, seguridad, login QA y PWA.
9. Conecta el proyecto staging a la nueva base.
10. Revoca credenciales temporales y elimina cualquier artefacto de copia.

### Resultado

Staging conserva datos representativos de Producción, pero ninguna sesión,
contraseña, privilegio ni token productivo permite autenticarse o validar una
credencial allí.
