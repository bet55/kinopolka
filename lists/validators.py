import os

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError


AVATARS_DIR = os.path.join("static", "img", "avatars")


def validate_avatar_path(value: str) -> None:
    """
    Аватарка — либо внешний URL, либо путь к существующему файлу в static.
    Django-валидатор (не DRF): срабатывает в формах админки.
    """
    if value.startswith(("http://", "https://")):
        return

    if not value.startswith("/static/") or not os.path.isfile(value.lstrip("/")):
        available = ", ".join(sorted(os.listdir(AVATARS_DIR)))
        raise DjangoValidationError(f"Файл не найден. Есть в /static/img/avatars/: {available}")


def validate_kp_id(field: int) -> None:
    if field is None:
        raise ValidationError("kp_id is required")


def validate_name(field: str) -> None:
    if field is None:
        raise ValidationError("Name is required")
