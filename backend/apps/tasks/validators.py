from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from PIL import Image, UnidentifiedImageError

from apps.tasks.constants import (
    ATTACHMENT_DIMENSIONS_ERROR_MESSAGE,
    ATTACHMENT_INVALID_IMAGE_ERROR_MESSAGE,
    ATTACHMENT_TOO_LARGE_ERROR_MESSAGE,
    ATTACHMENT_UNSUPPORTED_FORMAT_ERROR_MESSAGE,
)

MAX_ATTACHMENT_BYTES = 5 * 1024 * 1024
# Bound decoded pixels well under Pillow's ~89M default so a small file can't
# claim huge dimensions and blow up memory on decode (decompression bomb).
MAX_IMAGE_PIXELS = 24_000_000
ALLOWED_IMAGE_FORMATS = {"JPEG", "PNG", "GIF", "WEBP"}


def validate_attachment_size(value: UploadedFile) -> None:
    if value.size > MAX_ATTACHMENT_BYTES:
        raise ValidationError(ATTACHMENT_TOO_LARGE_ERROR_MESSAGE)


def validate_image_format(value: UploadedFile) -> None:
    try:
        with Image.open(value) as img:
            image_format = img.format
            pixels = img.width * img.height
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise ValidationError(ATTACHMENT_INVALID_IMAGE_ERROR_MESSAGE) from exc
    finally:
        value.seek(0)
    if image_format not in ALLOWED_IMAGE_FORMATS:
        raise ValidationError(ATTACHMENT_UNSUPPORTED_FORMAT_ERROR_MESSAGE)
    if pixels > MAX_IMAGE_PIXELS:
        raise ValidationError(ATTACHMENT_DIMENSIONS_ERROR_MESSAGE)
