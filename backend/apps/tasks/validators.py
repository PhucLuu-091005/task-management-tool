from django.core.exceptions import ValidationError
from PIL import Image, UnidentifiedImageError

MAX_ATTACHMENT_BYTES = 5 * 1024 * 1024
# Bound decoded pixels well under Pillow's ~89M default so a small file can't
# claim huge dimensions and blow up memory on decode (decompression bomb).
MAX_IMAGE_PIXELS = 24_000_000
ALLOWED_IMAGE_FORMATS = {"JPEG", "PNG", "GIF", "WEBP"}


def validate_attachment_size(value):
    if value.size > MAX_ATTACHMENT_BYTES:
        raise ValidationError("Image must be 5 MB or smaller.")


def validate_image_format(value):
    try:
        with Image.open(value) as img:
            image_format = img.format
            pixels = img.width * img.height
    except UnidentifiedImageError as exc:
        raise ValidationError("Upload a valid image.") from exc
    finally:
        value.seek(0)
    if image_format not in ALLOWED_IMAGE_FORMATS:
        raise ValidationError("Unsupported image format; use JPEG, PNG, GIF, or WEBP.")
    if pixels > MAX_IMAGE_PIXELS:
        raise ValidationError("Image dimensions are too large.")
