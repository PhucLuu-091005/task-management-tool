import os

from decouple import config

from .base import *

DEBUG = False

ALLOWED_HOSTS = [h for h in config("ALLOWED_HOSTS", default="").split(",") if h]
# Render injects the service's public hostname; trust it so the app boots even
# before ALLOWED_HOSTS is set by hand.
_render_host = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if _render_host:
    ALLOWED_HOSTS.append(_render_host)

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# TLS is terminated at the platform's proxy, so trust its forwarded scheme —
# without this Django sees plain HTTP and won't honour the Secure cookies below.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Auth/session/CSRF cookies must only travel over HTTPS in production.
AUTH_REFRESH_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

# gunicorn doesn't serve static files; WhiteNoise does. It sits right after
# SecurityMiddleware per WhiteNoise's documented ordering.
MIDDLEWARE = MIDDLEWARE[:2] + ["whitenoise.middleware.WhiteNoiseMiddleware"] + MIDDLEWARE[2:]
STATIC_ROOT = BASE_DIR / "staticfiles"

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
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
