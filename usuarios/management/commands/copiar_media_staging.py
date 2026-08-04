from pathlib import PurePosixPath
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError

from comercios.models import Comercio
from contenidos.models import Publicidad


MAX_MEDIA_BYTES = 10 * 1024 * 1024
ALLOWED_MEDIA_PREFIXES = ("comercios/", "publicidades/")


def _source_base_url(raw_url):
    value = str(raw_url).strip().rstrip("/")
    parsed = urlsplit(value)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
    ):
        raise CommandError("El origen de media debe ser una URL HTTPS sin credenciales.")
    return value


def _referenced_media_paths():
    paths = {
        *Comercio.objects.exclude(foto__isnull=True)
        .exclude(foto="")
        .values_list("foto", flat=True),
        *Publicidad.objects.exclude(foto="").values_list("foto", flat=True),
    }
    normalized_paths = []
    for raw_path in paths:
        path = str(raw_path).strip()
        pure_path = PurePosixPath(path)
        if (
            not path.startswith(ALLOWED_MEDIA_PREFIXES)
            or pure_path.is_absolute()
            or ".." in pure_path.parts
        ):
            raise CommandError(f'La referencia media "{path}" no es una ruta permitida.')
        normalized_paths.append(path)
    return sorted(normalized_paths)


def _download_image(source_base_url, media_path):
    source_url = f"{source_base_url}/{quote(media_path, safe='/')}"
    request = Request(source_url, headers={"User-Agent": "Uni2-Staging-Media-Copy/1.0"})
    with urlopen(request, timeout=30) as response:
        final_url = urlsplit(response.geturl())
        expected_url = urlsplit(source_base_url)
        if (
            final_url.scheme != expected_url.scheme
            or final_url.netloc != expected_url.netloc
        ):
            raise ValueError("el origen redirigió hacia otro dominio")

        content_type = response.headers.get("Content-Type", "").split(";", 1)[0]
        if not content_type.startswith("image/"):
            raise ValueError(f"el origen respondió {content_type or 'sin Content-Type'}")

        content = response.read(MAX_MEDIA_BYTES + 1)
        if len(content) > MAX_MEDIA_BYTES:
            raise ValueError("la imagen supera el límite de 10 MB")
        return content


class Command(BaseCommand):
    help = "Copia a un bucket staging las imágenes públicas referenciadas por su base."

    def add_arguments(self, parser):
        parser.add_argument("--source-base-url", required=True)
        parser.add_argument("--confirm-target", required=True)
        parser.add_argument(
            "--confirmar",
            action="store_true",
            help="Descarga y guarda los archivos. Sin esta opción sólo informa el plan.",
        )

    def handle(self, *args, **options):
        if getattr(settings, "UNI2_DEPLOYMENT_ENVIRONMENT", "") != "staging":
            raise CommandError("Este comando sólo puede ejecutarse con settings de staging.")
        if options["confirm_target"] != settings.UNI2_STAGING_DATABASE_LABEL:
            raise CommandError("La confirmación no coincide con la base staging configurada.")
        if (
            not getattr(settings, "AWS_STORAGE_BUCKET_NAME", "")
            or settings.STORAGES["default"]["BACKEND"]
            != "storages.backends.s3.S3Storage"
        ):
            raise CommandError("Staging no tiene un bucket media remoto configurado.")

        source_base_url = _source_base_url(options["source_base_url"])
        media_paths = _referenced_media_paths()
        self.stdout.write(f"Archivos referenciados: {len(media_paths)}")
        if not options["confirmar"]:
            self.stdout.write(
                self.style.WARNING(
                    "No se copiaron archivos. Repetí el comando con --confirmar."
                )
            )
            return

        copied = 0
        existing = 0
        errors = []
        for media_path in media_paths:
            if default_storage.exists(media_path):
                existing += 1
                continue

            try:
                content = _download_image(source_base_url, media_path)
                saved_path = default_storage.save(media_path, ContentFile(content))
                if saved_path != media_path:
                    default_storage.delete(saved_path)
                    raise ValueError("el storage intentó cambiar el nombre del archivo")
            except (HTTPError, URLError, OSError, ValueError) as exc:
                errors.append(f"{media_path}: {exc}")
                self.stderr.write(self.style.ERROR(errors[-1]))
            else:
                copied += 1

        summary = (
            f"Copia media: {copied} archivos copiados, "
            f"{existing} ya existentes y {len(errors)} errores."
        )
        if errors:
            raise CommandError(summary)
        self.stdout.write(self.style.SUCCESS(summary))
