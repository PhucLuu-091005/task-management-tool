"""
Fixtures share across test files declared here (no need to import)
"""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    # Pass in db to have DB access, if not, ORM error is raised
    return User.objects.create_user(
        email="lalu@example.com",
        username="laluu",
        password="LatotheLuungolZai@@@@@",
        first_name="La",
        last_name="Phuc",
    )


@pytest.fixture
def auth_client(api_client, user):
    # Compose 2 of the above to get auth user
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def valid_regis_payload():
    # A valid starting point so the later test can invalidate on field and test
    return {
        "email": "ahihi@example.com",
        "username": "ahihi",
        "password": "ahihi1234@@@@@",
        "first_name": "ahi",
        "last_name": "ho",
    }


# URL here for maintenance matters


@pytest.fixture
def register_url():
    return reverse("register")


@pytest.fixture
def profile_url():
    return reverse("profile")


@pytest.fixture
def logout_url():
    return reverse("logout")


@pytest.fixture
def login_url():
    return reverse("login")


# To check refresh token


@pytest.fixture
def refresh_token(user):
    return str(RefreshToken.for_user(user))
