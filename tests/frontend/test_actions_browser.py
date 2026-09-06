"""Pruebas con Chromium real y servidor local; sin dependencias JS adicionales."""
import json
import re
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import shutil
import subprocess
from threading import Thread

import pytest
from django.urls import reverse

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("mobile", [False, True], ids=["desktop", "mobile"])
@pytest.mark.django_db
def test_acciones_en_navegador(tmp_path, mobile, client):
    chromium = shutil.which("chromium") or shutil.which("chromium-browser")
    if not chromium:
        pytest.skip("Instalar Chromium para ejecutar las pruebas de navegador")
    requests = []
    preinscripcion = client.get(reverse("web:preinscripcion")).content

    class Handler(SimpleHTTPRequestHandler):
        def log_message(self, *_args):
            pass

        def do_POST(self):
            requests.append(self.rfile.read(int(self.headers["Content-Length"])).decode())
            self.send_response(204)
            self.end_headers()

        def do_GET(self):
            if self.path == "/preinscripcion":
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(preinscripcion)
            elif self.path == "/requests":
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(requests).encode())
            else:
                super().do_GET()

    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Handler, directory=str(ROOT)))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        result = subprocess.run([
            chromium, "--headless=new", "--no-sandbox", "--disable-gpu",
            f"--user-data-dir={tmp_path / 'chrome'}", "--no-proxy-server",
            "--window-size=390,844" if mobile else "--window-size=1280,900",
            "--touch-events=enabled" if mobile else "--touch-events=disabled",
            *(["--force-prefers-reduced-motion"] if mobile else []),
            "--virtual-time-budget=10000", "--dump-dom",
            f"http://127.0.0.1:{server.server_port}/tests/frontend/actions.html" + ("?mobile" if mobile else ""),
        ], capture_output=True, text=True, timeout=45)
        assert result.returncode == 0, result.stderr
        status = re.search(r'<pre id="results">(.*?)</pre>', result.stdout, re.S)
        assert status and status.group(1) == "PASS", status.group(1) if status else result.stdout
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
