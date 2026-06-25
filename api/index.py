import os


def app(environ, start_response):
    db_url = os.environ.get("DATABASE_URL", "no-encontrada")
    start_response("200 OK", [("Content-Type", "text/plain")])
    return [db_url.encode()]
