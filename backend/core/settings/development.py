from .base import *

DEBUG = True
# "backend" is the compose service name: the Next.js proxy forwards /api/* to
# http://backend:8000, so that Host must be allowed when running under Docker.
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "backend"]

# Open the API docs to anonymous users locally; production keeps base's authenticated default.
SPECTACULAR_SETTINGS = {
    **SPECTACULAR_SETTINGS,
    "SERVE_PERMISSIONS": ["rest_framework.permissions.AllowAny"],
}

# Display SQL statement for debugging purpose
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "loggers": {
        "django.db.backends": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
    },
}
