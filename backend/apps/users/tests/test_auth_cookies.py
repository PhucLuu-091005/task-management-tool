import pytest
from django.conf import settings
from rest_framework.test import APIClient


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


@pytest.mark.django_db
def test_csrf_endpoint_sets_cookie(api_client, csrf_url):
    res = api_client.get(csrf_url)
    assert res.status_code == 204
    assert "csrftoken" in res.cookies


@pytest.mark.django_db
def test_refresh_reads_cookie_rotates_and_resets(login_url, refresh_url, csrf_url, login_payload):
    client = APIClient(enforce_csrf_checks=True)
    client.post(login_url, login_payload, format="json")
    client.get(csrf_url)
    token = client.cookies["csrftoken"].value

    res = client.post(refresh_url, {}, format="json", HTTP_X_CSRFTOKEN=token)

    assert res.status_code == 200
    assert "access" in res.data
    assert "refresh" not in res.data
    assert settings.AUTH_REFRESH_COOKIE in res.cookies


@pytest.mark.django_db
def test_refresh_without_cookie_returns_401(refresh_url, csrf_url):
    client = APIClient(enforce_csrf_checks=True)
    client.get(csrf_url)
    token = client.cookies["csrftoken"].value

    res = client.post(refresh_url, {}, format="json", HTTP_X_CSRFTOKEN=token)

    assert res.status_code == 401


@pytest.mark.django_db
def test_refresh_without_csrf_returns_403(login_url, refresh_url, login_payload):
    client = APIClient(enforce_csrf_checks=True)
    client.post(login_url, login_payload, format="json")

    res = client.post(refresh_url, {}, format="json")

    assert res.status_code == 403


@pytest.mark.django_db
def test_old_refresh_is_blacklisted_after_rotation(login_url, refresh_url, csrf_url, login_payload):
    client = APIClient(enforce_csrf_checks=True)
    client.post(login_url, login_payload, format="json")
    old_refresh = client.cookies[settings.AUTH_REFRESH_COOKIE].value
    client.get(csrf_url)
    token = client.cookies["csrftoken"].value

    first = client.post(refresh_url, {}, format="json", HTTP_X_CSRFTOKEN=token)
    assert first.status_code == 200

    client.cookies[settings.AUTH_REFRESH_COOKIE] = old_refresh
    reuse = client.post(refresh_url, {}, format="json", HTTP_X_CSRFTOKEN=token)
    assert reuse.status_code == 401
