from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from PIL import Image, UnidentifiedImageError

from apps.users.constants import (
    AVATAR_DIMENSIONS_ERROR_MESSAGE,
    AVATAR_INVALID_IMAGE_ERROR_MESSAGE,
    AVATAR_TOO_LARGE_ERROR_MESSAGE,
    AVATAR_UNSUPPORTED_FORMAT_ERROR_MESSAGE,
)

MAX_AVATAR_BYTES = 2 * 1024 * 1024
# Bound decoded pixels well under Pillow's ~89M default so a small file can't
# claim huge dimensions and blow up memory on decode (decompression bomb).
MAX_IMAGE_PIXELS = 24_000_000
ALLOWED_IMAGE_FORMATS = {"JPEG", "PNG", "GIF", "WEBP"}


def validate_avatar_size(value: UploadedFile) -> None:
    if value.size > MAX_AVATAR_BYTES:
        raise ValidationError(AVATAR_TOO_LARGE_ERROR_MESSAGE)


def validate_avatar_image(value: UploadedFile) -> None:
    try:
        with Image.open(value) as img:
            image_format = img.format
            pixels = img.width * img.height
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise ValidationError(AVATAR_INVALID_IMAGE_ERROR_MESSAGE) from exc
    finally:
        value.seek(0)
    if image_format not in ALLOWED_IMAGE_FORMATS:
        raise ValidationError(AVATAR_UNSUPPORTED_FORMAT_ERROR_MESSAGE)
    if pixels > MAX_IMAGE_PIXELS:
        raise ValidationError(AVATAR_DIMENSIONS_ERROR_MESSAGE)
