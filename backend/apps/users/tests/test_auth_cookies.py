import pytest
from django.conf import settings


@pytest.mark.django_db
def test_login_sets_httponly_refresh_cookie_and_omits_it_from_body(
    api_client, login_url, login_payload
):
    res = api_client.post(login_url, login_payload, format="json")

    assert res.status_code == 200
    assert "access" in res.data
    assert "refresh" not in res.data

    cookie = res.cookies.get(settings.AUTH_REFRESH_COOKIE)
    assert cookie is not None
    assert cookie["httponly"]
    assert cookie["samesite"] == "Strict"
    assert cookie["path"] == settings.AUTH_REFRESH_COOKIE_PATH
    assert not cookie["secure"]
