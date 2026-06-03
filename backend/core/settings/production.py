from decouple import config

from .base import *

DEBUG = False
ALLOWED_HOSTS = config("ALLOWED_HOSTS").split(",")

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
