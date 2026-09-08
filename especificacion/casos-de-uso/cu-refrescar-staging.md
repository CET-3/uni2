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
5. El sistema elimina las sesiones copiadas y conserva sin cambios los
   usuarios, contraseñas, grupos, permisos, privilegios, perfiles y tokens.
6. Como último paso transaccional, el sistema escribe el marcador del refresh.
7. La responsable verifica conteos, igualdad de usuarios, readiness, seguridad,
   login controlado y PWA.
8. Conecta el proyecto staging a la nueva base.
9. Revoca credenciales temporales y elimina cualquier artefacto de copia.

### Resultado

Staging conserva una copia fiel de las cuentas de Producción, incluidas sus
contraseñas, privilegios y tokens. Por eso las credenciales productivas también
son válidas en staging: el acceso permanece protegido por la barrera HTTP, la
base está aislada y los canales de correo y push están deshabilitados.

## Rotación posterior de credenciales QA

La rotación de contraseñas QA es un flujo separado para un staging que ya tenga
cuentas QA ficticias. No forma parte de este refresco fiel y no debe ejecutarse
para reemplazar ni modificar las cuentas copiadas de Producción.
