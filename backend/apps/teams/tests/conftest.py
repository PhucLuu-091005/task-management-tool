import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.teams.models import Team

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_user(db):
    return User.objects.create_user(
        email="admin@example.com",
        username="admin",
        password="Str0ng!Passw0rd",
        is_admin=True,
    )


@pytest.fixture
def member_user(db):
    return User.objects.create_user(
        email="member@example.com", username="member", password="Str0ng!Passw0rd"
    )


@pytest.fixture
def admin_client(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def member_client(api_client, member_user):
    api_client.force_authenticate(user=member_user)
    return api_client


@pytest.fixture
def team(db):
    return Team.objects.create(name="Alpha")
