import pytest
from django.contrib.auth import get_user_model

from apps.teams.models import Department, Team, TeamMembership
from apps.users.constants import (
    EMAIL_UNIQUE_ERROR_MESSAGE,
    USERNAME_CONTENT_ERROR_MESSAGE,
    USERNAME_UNIQUE_ERROR_MESSAGE,
)
from apps.users.serializers import RegisterSerializer, UserSerializer

User = get_user_model()

# Every RegisterSerializer.is_valid() runs UniqueValidator, which queries the DB,
# so the whole module needs DB access.
pytestmark = pytest.mark.django_db


def test_valid_payload_passes(valid_regis_payload):
    assert RegisterSerializer(data=valid_regis_payload).is_valid()


def test_email_is_lowercased(valid_regis_payload):
    serializer = RegisterSerializer(
        data={**valid_regis_payload, "email": valid_regis_payload["email"].upper()}
    )
    assert serializer.is_valid()
    assert serializer.validated_data["email"] == valid_regis_payload["email"]


@pytest.mark.parametrize("bad_username", ["laluu@", "la luu", "la-luu", "la_luu"])
def test_username_with_special_character(valid_regis_payload, bad_username):
    serializer = RegisterSerializer(data={**valid_regis_payload, "username": bad_username})
    assert serializer.is_valid() is False
    assert "username" in serializer.errors
    assert USERNAME_CONTENT_ERROR_MESSAGE in serializer.errors["username"]


@pytest.mark.parametrize("weak_password", ["12345678", "password", "1"])
def test_weak_password_rejected(valid_regis_payload, weak_password):
    serializer = RegisterSerializer(data={**valid_regis_payload, "password": weak_password})
    assert serializer.is_valid() is False
    assert "password" in serializer.errors


def test_password_same_username_rejected(valid_regis_payload):
    serializer = RegisterSerializer(
        data={**valid_regis_payload, "password": valid_regis_payload["username"]}
    )
    assert serializer.is_valid() is False
    assert "password" in serializer.errors


# Test uniqueness


def test_email_unique(valid_regis_payload):
    # Raise exception here so we now that this test went wrong in the setup step
    RegisterSerializer(data=valid_regis_payload).is_valid(raise_exception=True)
    User.objects.create_user(**valid_regis_payload)
    serializer = RegisterSerializer(
        data={**valid_regis_payload, "username": "test_email_unique_serializer"}
    )
    assert serializer.is_valid() is False
    assert "email" in serializer.errors
    assert EMAIL_UNIQUE_ERROR_MESSAGE in serializer.errors["email"]


@pytest.mark.django_db
def test_username_unique(valid_regis_payload):
    # Raise exception here so we now that this test went wrong in the setup step
    RegisterSerializer(data=valid_regis_payload).is_valid(raise_exception=True)
    User.objects.create_user(**valid_regis_payload)
    serializer = RegisterSerializer(
        data={**valid_regis_payload, "email": "testusername@serializer.com"}
    )
    assert serializer.is_valid() is False
    assert "username" in serializer.errors
    assert USERNAME_UNIQUE_ERROR_MESSAGE in serializer.errors["username"]


# Test hide password from output


@pytest.mark.django_db
def test_register_serializer_output_hides_password(valid_regis_payload):
    serializer = RegisterSerializer(data=valid_regis_payload)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    output = RegisterSerializer(user).data
    assert "password" not in output


# Test create valid and wires up to create_user


@pytest.mark.django_db
def test_create_return_persisted_user_hashed_password(valid_regis_payload):
    serializer = RegisterSerializer(data=valid_regis_payload)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    assert user.pk is not None
    assert user.email == valid_regis_payload["email"].lower()
    assert user.check_password(valid_regis_payload["password"])
    assert user.password != valid_regis_payload["password"]


# Test missing field


@pytest.mark.parametrize("miss_field", ["email", "username", "password", "first_name", "last_name"])
def test_missing_field(valid_regis_payload, miss_field):
    valid_regis_payload.pop(miss_field)
    serializer = RegisterSerializer(data=valid_regis_payload)
    assert serializer.is_valid() is False
    assert miss_field in serializer.errors


# Test UserSerializer


@pytest.mark.django_db
def test_user_serializer_output_hides_password(user):
    data = UserSerializer(user).data
    assert "password" not in data
    assert set(data.keys()) == {
        "id",
        "email",
        "username",
        "first_name",
        "last_name",
        "is_admin",
        "avatar",
        "memberships",
    }


# is_admin + team memberships exposed in the user API (A3)


def test_user_serializer_includes_is_admin(user):
    data = UserSerializer(user).data
    assert data["is_admin"] is False


def test_user_serializer_lists_team_memberships(user):
    dept = Department.objects.create(name="Dept Serializer Alpha")
    team = Team.objects.create(name="Alpha", department=dept)
    TeamMembership.objects.create(user=user, team=team, role=TeamMembership.Role.LEADER)
    data = UserSerializer(user).data
    assert data["memberships"] == [{"team": team.id, "team_name": "Alpha", "role": "leader"}]
