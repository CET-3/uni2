from django.conf import settings
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.http import Http404, JsonResponse


def _migrations_are_current():
    executor = MigrationExecutor(connection)
    return not executor.migration_plan(executor.loader.graph.leaf_nodes())


def staging_readiness(request):
    if settings.UNI2_DEPLOYMENT_ENVIRONMENT != "staging":
        raise Http404

    state = getattr(request, "uni2_staging_data_state", None)
    if state is None:
        raise Http404

    migrations_current = _migrations_are_current()
    return JsonResponse(
        {
            "build_id": settings.PWA_BUILD_ID,
            "data_epoch": state.refresh_id,
            "environment": "staging",
            "migrations_current": migrations_current,
            "ready": migrations_current,
        },
        status=200 if migrations_current else 503,
    )
