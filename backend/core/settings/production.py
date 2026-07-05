from decouple import config

from .base import *

DEBUG = False
ALLOWED_HOSTS = config("ALLOWED_HOSTS").split(",")

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Attachment uploads go to a private S3 bucket; images are served via time-limited
# presigned URLs. Credentials come from AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY in
# the environment or an attached IAM role — never hard-coded here.
AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = config("AWS_S3_REGION_NAME", default="")
AWS_S3_ENDPOINT_URL = config("AWS_S3_ENDPOINT_URL", default="") or None
AWS_PRESIGNED_EXPIRY = config("AWS_PRESIGNED_EXPIRY", default=3600, cast=int)

STORAGES = {
    **STORAGES,
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "bucket_name": AWS_STORAGE_BUCKET_NAME,
            "region_name": AWS_S3_REGION_NAME or None,
            "endpoint_url": AWS_S3_ENDPOINT_URL,
            "signature_version": "s3v4",
            "default_acl": None,
            "querystring_auth": True,
            "querystring_expire": AWS_PRESIGNED_EXPIRY,
            "file_overwrite": False,
        },
    },
}
