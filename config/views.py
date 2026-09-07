from django.conf import settings
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.http import Http404, JsonResponse


def _pending_migration_names():
    executor = MigrationExecutor(connection)
    return [
        f"{migration.app_label}.{migration.name}"
        for migration, backwards in executor.migration_plan(
            executor.loader.graph.leaf_nodes()
        )
        if not backwards
    ]


def staging_readiness(request):
    if settings.UNI2_DEPLOYMENT_ENVIRONMENT != "staging":
        raise Http404

    state = getattr(request, "uni2_staging_data_state", None)
    if state is None:
        raise Http404

    pending_migrations = _pending_migration_names()
    migrations_current = not pending_migrations
    payload = {
        "build_id": settings.PWA_BUILD_ID,
        "data_epoch": state.refresh_id,
        "environment": "staging",
        "migrations_current": migrations_current,
        "pending_migrations": pending_migrations,
        "ready": migrations_current,
    }
    if pending_migrations:
        payload["reason"] = "migrations_pending"
    return JsonResponse(
        payload,
        status=200 if migrations_current else 503,
    )
