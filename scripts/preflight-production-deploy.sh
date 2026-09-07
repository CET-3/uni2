#!/usr/bin/env bash

set -euo pipefail

usage() {
    cat <<'EOF'
Uso:
  scripts/preflight-production-deploy.sh [--env-file ARCHIVO] [--apply]

Por defecto sólo muestra el plan de migraciones. --apply aplica las migraciones
y vuelve a comprobar que no queden operaciones pendientes.
EOF
}

env_file=".env.production"
apply_migrations=false

while (($#)); do
    case "$1" in
        --env-file)
            [[ $# -ge 2 ]] || { echo "Falta el archivo después de --env-file" >&2; exit 2; }
            env_file="$2"
            shift 2
            ;;
        --apply)
            apply_migrations=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Argumento desconocido: $1" >&2
            usage >&2
            exit 2
            ;;
    esac
done

[[ -f "$env_file" ]] || { echo "No existe $env_file" >&2; exit 1; }

django_env=(
    SECRET_KEY="${SECRET_KEY:-preflight-only-secret}"
    UNI2_TRANSACTIONAL_EMAIL_MODE=disabled
    DJANGO_SETTINGS_MODULE=config.settings.production
)

run_manage() {
    uv run --env-file "$env_file" -- env "${django_env[@]}" python manage.py "$@"
}

echo "Verificando que no falten migraciones en los modelos..."
run_manage makemigrations --check --dry-run

echo "Plan de migraciones productivas:"
run_manage migrate --plan

if [[ "$apply_migrations" != true ]]; then
    echo "Preflight terminado sin aplicar migraciones. Usá --apply para aplicarlas."
    exit 0
fi

echo "Aplicando migraciones productivas..."
run_manage migrate --noinput

echo "Verificando que no queden migraciones pendientes..."
plan="$(run_manage migrate --plan)"
printf '%s\n' "$plan"
grep -q "No planned migration operations\." <<<"$plan" || {
    echo "Quedaron migraciones pendientes después de aplicar." >&2
    exit 1
}

echo "Preflight productivo aprobado."
