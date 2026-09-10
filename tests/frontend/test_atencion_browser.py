"""Prueba opcional de Atención diaria con Django y Chromium reales."""

import os
from pathlib import Path
import shutil
import subprocess
import time

import pytest
from django.utils import timezone

from cuotas.models import Donacion, Pago
from gestion.tests.test_atencion_diaria import pago, persona, usuario


@pytest.mark.browser
@pytest.mark.django_db(transaction=True)
def test_atencion_responsive_temas_y_filtros(live_server, client, tmp_path):
    chrome = shutil.which("google-chrome") or shutil.which("chromium")
    node = os.environ.get("UNI2_BROWSER_NODE") or shutil.which("node")
    if not chrome or not node:
        pytest.skip("Requiere Chromium y Node 22+ (UNI2_BROWSER_NODE).")
    supports_websocket = subprocess.run([node, "-e", "process.exit(typeof WebSocket === 'function' ? 0 : 1)"], capture_output=True)
    if supports_websocket.returncode:
        pytest.skip("El runner CDP requiere Node 22+; indicar UNI2_BROWSER_NODE.")
    user = usuario(consultar=True, equipo=True)
    a = persona(fecha=timezone.localdate())
    for amount, method in (("10000.25", Pago.METODO_EFECTIVO), ("20000.50", Pago.METODO_BILLETERA)):
        p = pago(a, user, amount, fecha=timezone.localdate(), metodo=method)
        Donacion.objects.create(asociado=a,pago=p,fecha=p.fecha,importe=amount)
    client.force_login(user)
    profile = tmp_path / "chrome"
    with (tmp_path / "chrome.log").open("w") as log:
        browser = subprocess.Popen([
            chrome, "--headless=new", "--no-sandbox", "--disable-gpu",
            "--disable-background-networking", "--no-proxy-server",
            "--remote-debugging-port=0", f"--user-data-dir={profile}", "about:blank",
        ], stdout=log, stderr=log)
        try:
            port_file = profile / "DevToolsActivePort"
            for _ in range(100):
                if port_file.exists():
                    break
                time.sleep(.05)
            assert port_file.exists(), (tmp_path / "chrome.log").read_text()[-2000:]
            port = port_file.read_text().splitlines()[0]
            runner = Path(__file__).with_name("atencion-browser.cjs")
            result = subprocess.run(
                [node, str(runner), port, live_server.url, str(tmp_path)],
                env={**os.environ, "UNI2_TEST_SESSION": client.cookies["sessionid"].value},
                capture_output=True, text=True, timeout=40,
            )
            assert result.returncode == 0, result.stdout + result.stderr
        finally:
            browser.terminate()
            try:
                browser.wait(timeout=5)
            except subprocess.TimeoutExpired:
                browser.kill()
                browser.wait(timeout=5)
