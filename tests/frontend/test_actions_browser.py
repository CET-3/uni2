"""Pruebas con Chromium real y servidor local; sin dependencias JS adicionales."""
import json
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import shutil
import subprocess
from threading import Event, Thread

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
    completed = Event()
    results = []
    preinscripcion = client.get(reverse("web:preinscripcion")).content

    class Handler(SimpleHTTPRequestHandler):
        def log_message(self, *_args):
            pass

        def do_POST(self):
            body = self.rfile.read(int(self.headers["Content-Length"])).decode()
            if self.path == "/test-result":
                results.append(body)
                completed.set()
            else:
                requests.append(body)
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
        command = [
            chromium, "--headless=new", "--no-sandbox", "--disable-gpu",
            f"--user-data-dir={tmp_path / 'chrome'}", "--no-proxy-server",
            "--window-size=390,844" if mobile else "--window-size=1280,900",
            "--touch-events=enabled" if mobile else "--touch-events=disabled",
            *(["--force-prefers-reduced-motion"] if mobile else []),
            "--remote-debugging-port=0", "--disable-background-networking",
            f"http://127.0.0.1:{server.server_port}/tests/frontend/actions.html" + ("?mobile" if mobile else ""),
        ]
        # La página informa su resultado; no dependemos de que Chromium cierre
        # dump-dom ni del reloj virtual para terminar pruebas con iframes/PWA.
        log_path = tmp_path / "chromium.log"
        with log_path.open("w") as log:
            process = subprocess.Popen(command, stdout=log, stderr=log)
            try:
                assert completed.wait(45), (
                    f"El navegador no informó resultado; POST recibidos: {len(requests)}.\n"
                    + log_path.read_text()[-6000:]
                )
                assert results == ["PASS"], results
            finally:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
