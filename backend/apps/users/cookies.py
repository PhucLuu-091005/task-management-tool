from django.conf import settings
from django.http import HttpResponse


def set_refresh_cookie(response: HttpResponse, token: str) -> None:
    response.set_cookie(
        settings.AUTH_REFRESH_COOKIE,
        token,
        max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
        httponly=settings.AUTH_REFRESH_COOKIE_HTTPONLY,
        secure=settings.AUTH_REFRESH_COOKIE_SECURE,
        samesite=settings.AUTH_REFRESH_COOKIE_SAMESITE,
        path=settings.AUTH_REFRESH_COOKIE_PATH,
    )


def delete_refresh_cookie(response: HttpResponse) -> None:
    response.delete_cookie(
        settings.AUTH_REFRESH_COOKIE,
        path=settings.AUTH_REFRESH_COOKIE_PATH,
        samesite=settings.AUTH_REFRESH_COOKIE_SAMESITE,
    )
