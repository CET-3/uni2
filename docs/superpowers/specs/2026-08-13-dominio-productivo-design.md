# Diseño: dominio productivo de Uni2

## Objetivo

Actualizar la documentación para reflejar la configuración productiva vigente:

- `https://www.uni2.app/` es la URL pública canónica.
- `https://uni2.app/` redirige hacia la URL canónica.
- `https://uni2-ashy.vercel.app/` continúa admitida como dirección técnica
  secundaria, pero no se presenta como acceso público principal.

## Alcance

La actualización se limita a documentación. No requiere cambios en Django,
URLs, templates ni configuración versionada porque los hosts y orígenes se
inyectan mediante variables del entorno Production de Vercel.

Se modificarán:

- `README.md`, para mostrar la dirección pública actual.
- `especificacion/arquitectura/despliegue.md`, para documentar el dominio
  canónico, la redirección, la responsabilidad de Porkbun y Vercel, y la
  dirección técnica secundaria.
- `especificacion/arquitectura/deploy.md`, para registrar los valores no
  secretos requeridos en `ALLOWED_HOSTS` y `CSRF_TRUSTED_ORIGINS`.

## Configuración documentada

Porkbun conserva los nameservers autoritativos y administra los registros DNS.
El dominio raíz usa el registro `A` indicado por Vercel y `www` usa el `CNAME`
específico asignado al proyecto. Vercel termina HTTPS, publica la aplicación y
redirige el dominio raíz hacia `www`.

Production debe admitir estos hosts:

```text
uni2.app,www.uni2.app,uni2-ashy.vercel.app
```

Y estos orígenes CSRF:

```text
https://uni2.app,https://www.uni2.app,https://uni2-ashy.vercel.app
```

## Verificación

- Buscar referencias al dominio anterior y comprobar que ninguna lo describa
  como dominio público principal.
- Revisar que las tres páginas sean consistentes sobre dominio canónico,
  redirección y dirección técnica.
- Revisar el diff para confirmar que no haya cambios de código.
