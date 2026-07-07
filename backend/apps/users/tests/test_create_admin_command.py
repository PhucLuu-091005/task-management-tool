from io import StringIO

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command

User = get_user_model()


@pytest.fixture
def clear_admin_env(monkeypatch):
    for key in ("INITIAL_ADMIN_USERNAME", "INITIAL_ADMIN_PASSWORD", "INITIAL_ADMIN_EMAIL"):
        monkeypatch.delenv(key, raising=False)


@pytest.mark.django_db
def test_creates_admin_when_env_set(monkeypatch, clear_admin_env):
    monkeypatch.setenv("INITIAL_ADMIN_USERNAME", "boss")
    monkeypatch.setenv("INITIAL_ADMIN_PASSWORD", "Str0ng!Passw0rd")

    out = StringIO()
    call_command("create_admin", stdout=out)

    user = User.objects.get(username="boss")
    assert user.is_admin is True
    assert user.check_password("Str0ng!Passw0rd")
    assert "boss" in out.getvalue()


@pytest.mark.django_db
def test_skips_when_env_missing(clear_admin_env):
    out = StringIO()
    call_command("create_admin", stdout=out)

    assert User.objects.count() == 0
    assert "INITIAL_ADMIN" in out.getvalue()
