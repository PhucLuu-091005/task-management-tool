import pytest
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.teams.models import Team, TeamMembership

User = get_user_model()

# Register


@pytest.mark.django_db
def test_register_return_201_and_user(api_client, register_url, valid_regis_payload):
    res = api_client.post(register_url, valid_regis_payload)
    assert res.status_code == 201
    assert res.data["email"] == valid_regis_payload["email"].lower()
    assert "password" not in res.data
    assert User.objects.filter(email=valid_regis_payload["email"].lower()).exists()


@pytest.mark.django_db
def test_return_400_for_invalid_data(api_client, register_url, valid_regis_payload):
    res = api_client.post(
        register_url, {**valid_regis_payload, "password": valid_regis_payload["email"]}
    )
    assert res.status_code == 400
    assert "password" in res.data


def test_registrer_no_need_auth(api_client, register_url):
    res = api_client.post(register_url, {}, format="json")
    assert res.status_code == 400


# Profile test


@pytest.mark.django_db
def test_profile_return_valid_user(auth_client, profile_url, user):
    res = auth_client.get(profile_url)

    assert res.status_code == 200
    assert res.data["email"] == user.email
    assert res.data["username"] == user.username
    assert "password" not in res.data


def test_profile_return_401_for_unauthenticated_user(api_client, profile_url):
    res = api_client.get(profile_url)
    assert res.status_code == 401


@pytest.mark.django_db
def test_profile_avoids_n_plus_1_for_memberships(
    auth_client, profile_url, user, django_assert_max_num_queries
):
    for i in range(10):
        team = Team.objects.create(name=f"Team {i}")
        TeamMembership.objects.create(user=user, team=team, role=TeamMembership.Role.MEMBER)

    # Query count must stay flat regardless of how many memberships the user has.
    with django_assert_max_num_queries(4):
        res = auth_client.get(profile_url)

    assert res.status_code == 200
    assert len(res.data["memberships"]) == 10


# Logout test


@pytest.mark.django_db
def test_logout_blacklist_token(auth_client, logout_url, refresh_token):
    res = auth_client.post(logout_url, {"refresh": refresh_token}, format="json")
    assert res.status_code == 205
    with pytest.raises(TokenError):
        RefreshToken(refresh_token).verify()


@pytest.mark.django_db
def test_logout_without_refresh_token(auth_client, logout_url):
    res = auth_client.post(logout_url, {}, format="json")
    assert res.status_code == 400
    assert "refresh" in res.data


@pytest.mark.django_db
def test_logout_requires_auth(api_client, logout_url):
    res = api_client.post(logout_url, {"refresh": "anything"}, format="json")
    assert res.status_code == 401


# User list (admin)


@pytest.mark.django_db
def test_admin_lists_users_with_memberships(
    admin_client, admin_user, user, user_list_url, django_assert_max_num_queries
):
    for i in range(5):
        team = Team.objects.create(name=f"T{i}")
        TeamMembership.objects.create(user=user, team=team, role=TeamMembership.Role.MEMBER)

    with django_assert_max_num_queries(5):
        res = admin_client.get(user_list_url)

    assert res.status_code == 200
    assert {admin_user.id, user.id} <= {u["id"] for u in res.data}
    target = next(u for u in res.data if u["id"] == user.id)
    assert len(target["memberships"]) == 5


@pytest.mark.django_db
def test_user_list_requires_admin(auth_client, user_list_url):
    res = auth_client.get(user_list_url)
    assert res.status_code == 403


def test_user_list_requires_auth(api_client, user_list_url):
    res = api_client.get(user_list_url)
    assert res.status_code == 401


# Full auth flow


@pytest.mark.django_db
def test_full_auth_flow(api_client, register_url, login_url, profile_url, valid_regis_payload):
    r1 = api_client.post(register_url, valid_regis_payload, format="json")
    assert r1.status_code == 201

    r2 = api_client.post(
        login_url,
        {
            "username": valid_regis_payload["username"],
            "password": valid_regis_payload["password"],
        },
        format="json",
    )
    assert r2.status_code == 200
    access_token = r2.data["access"]

    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    r3 = api_client.get(profile_url)
    assert r3.status_code == 200
    assert r3.data["email"] == valid_regis_payload["email"].lower()
