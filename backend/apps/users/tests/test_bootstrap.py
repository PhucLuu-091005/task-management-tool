import pytest
from django.contrib.auth import get_user_model

from apps.users.bootstrap import seed_admin_from_env

User = get_user_model()


@pytest.mark.django_db
def test_no_credentials_creates_no_user():
    result = seed_admin_from_env(User, env={})

    assert result is None
    assert User.objects.count() == 0


@pytest.mark.django_db
def test_creates_admin_from_env():
    env = {
        "INITIAL_ADMIN_USERNAME": "boss",
        "INITIAL_ADMIN_PASSWORD": "Str0ng!Passw0rd",
        "INITIAL_ADMIN_EMAIL": "boss@corp.com",
    }

    user = seed_admin_from_env(User, env=env)

    assert user.username == "boss"
    assert user.email == "boss@corp.com"
    assert user.is_admin is True
    assert user.is_active is True
    assert user.check_password("Str0ng!Passw0rd")


@pytest.mark.django_db
def test_defaults_email_when_not_provided():
    env = {
        "INITIAL_ADMIN_USERNAME": "boss",
        "INITIAL_ADMIN_PASSWORD": "Str0ng!Passw0rd",
    }

    user = seed_admin_from_env(User, env=env)

    assert user.email == "boss@example.com"


@pytest.mark.django_db
def test_promotes_existing_user_and_resets_password():
    User.objects.create_user(
        username="boss",
        email="old@corp.com",
        password="OldPassw0rd!",
        first_name="B",
        last_name="Oss",
    )

    env = {
        "INITIAL_ADMIN_USERNAME": "boss",
        "INITIAL_ADMIN_PASSWORD": "New!Passw0rd",
    }
    user = seed_admin_from_env(User, env=env)

    assert User.objects.count() == 1
    assert user.is_admin is True
    assert user.check_password("New!Passw0rd")
