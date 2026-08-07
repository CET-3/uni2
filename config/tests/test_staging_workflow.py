import re
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]


def test_ci_reutilizable_valida_sqlite_y_postgresql():
    tests_workflow = (BASE_DIR / ".github/workflows/tests.yml").read_text()

    assert "workflow_call:" in tests_workflow
    assert "pytest (SQLite)" in tests_workflow
    assert "Endurecimiento staging (PostgreSQL)" in tests_workflow
    assert "image: postgres:16" in tests_workflow
    assert "-k preparar_copia_staging" in tests_workflow


def test_deploy_staging_nace_del_push_y_espera_los_tests():
    workflow = (BASE_DIR / ".github/workflows/deploy-staging.yml").read_text()

    assert "  push:" in workflow
    assert "      - staging" in workflow
    assert "uses: ./.github/workflows/tests.yml" in workflow
    assert "needs: tests" in workflow
    assert "workflow_run:" not in workflow


def test_deploy_apunta_al_proyecto_staging_y_promueve_despues_del_smoke():
    workflow = (BASE_DIR / ".github/workflows/deploy-staging.yml").read_text()

    assert "VERCEL_PROJECT_ID: ${{ secrets.VERCEL_STAGING_PROJECT_ID }}" in workflow
    assert "environment: staging" in workflow
    assert "--skip-domain" in workflow
    assert '--scope="$VERCEL_ORG_ID"' in workflow
    assert "STAGING_ACCESS_PASSWORD" in workflow
    assert ' curl "$path"' in workflow
    assert "VERCEL_AUTOMATION_BYPASS_SECRET" not in workflow
    assert "x-vercel-protection-bypass" not in workflow
    assert workflow.index("Probar seguridad, base, manifest y service worker") < workflow.index(
        "Promover el deployment aprobado"
    )
    assert workflow.index("Promover el deployment aprobado") < workflow.index(
        "Verificar el dominio estable promovido"
    )
    assert "/__staging__/readiness/" in workflow
    assert 'test "$anonymous_status" = "401"' in workflow
    assert 'data["build_id"] == os.environ["PWA_BUILD_ID"]' in workflow
    assert 'assert f"{width}x{height}" == sys.argv[1]' in workflow
    assert "STAGING_BASE_URL: ${{ vars.STAGING_BASE_URL }}" in workflow
    pwa_public_block = workflow.split('vercel_request "/manifest.webmanifest"', 1)[1].split(
        "- name: Promover el deployment aprobado",
        1,
    )[0]
    assert '--user "$STAGING_ACCESS_USERNAME:$STAGING_ACCESS_PASSWORD"' not in pwa_public_block


def test_deploy_descarga_un_sha_completo_de_checkout():
    workflow = (BASE_DIR / ".github/workflows/deploy-staging.yml").read_text()
    checkout_references = re.findall(r"actions/checkout@([0-9a-f]+)", workflow)

    assert checkout_references
    assert all(len(reference) == 40 for reference in checkout_references)
    assert "ref: ${{ github.sha }}" in workflow
