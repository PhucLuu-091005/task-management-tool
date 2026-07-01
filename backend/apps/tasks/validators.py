from django.core.exceptions import ValidationError
from PIL import Image, UnidentifiedImageError

MAX_ATTACHMENT_BYTES = 5 * 1024 * 1024
ALLOWED_IMAGE_FORMATS = {"JPEG", "PNG", "GIF", "WEBP"}


def validate_attachment_size(value):
    if value.size > MAX_ATTACHMENT_BYTES:
        raise ValidationError("Image must be 5 MB or smaller.")


def validate_image_format(value):
    try:
        with Image.open(value) as img:
            image_format = img.format
    except UnidentifiedImageError as exc:
        raise ValidationError("Upload a valid image.") from exc
    finally:
        value.seek(0)
    if image_format not in ALLOWED_IMAGE_FORMATS:
        raise ValidationError("Unsupported image format; use JPEG, PNG, GIF, or WEBP.")
