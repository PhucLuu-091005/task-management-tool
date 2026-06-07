"""Unit tests for the RBAC permission classes (A5), exercised directly."""

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework.test import APIRequestFactory

from apps.teams.models import Team, TeamMembership
from apps.users.permissions import IsAdmin, IsTeamLeader, IsTeamMember

User = get_user_model()

pytestmark = pytest.mark.django_db


@pytest.fixture
def make_request():
    factory = APIRequestFactory()

    def _make(user):
        request = factory.get("/")
        request.user = user
        return request

    return _make


@pytest.fixture
def admin_user():
    return User.objects.create_user(
        email="admin@example.com", username="admin", password="Str0ng!Passw0rd", is_admin=True
    )


@pytest.fixture
def plain_user():
    return User.objects.create_user(
        email="plain@example.com", username="plain", password="Str0ng!Passw0rd"
    )


@pytest.fixture
def team():
    return Team.objects.create(name="Alpha")


# --- IsAdmin ---


def test_is_admin_allows_admin(make_request, admin_user):
    assert IsAdmin().has_permission(make_request(admin_user), None) is True


def test_is_admin_denies_non_admin(make_request, plain_user):
    assert IsAdmin().has_permission(make_request(plain_user), None) is False


def test_is_admin_denies_anonymous(make_request):
    assert IsAdmin().has_permission(make_request(AnonymousUser()), None) is False


def test_is_admin_object_permission_follows_flag(make_request, admin_user, plain_user, team):
    assert IsAdmin().has_object_permission(make_request(admin_user), None, team) is True
    assert IsAdmin().has_object_permission(make_request(plain_user), None, team) is False


# --- IsTeamLeader ---


def test_team_leader_allows_leader_of_target_team(make_request, plain_user, team):
    TeamMembership.objects.create(user=plain_user, team=team, role=TeamMembership.Role.LEADER)
    assert IsTeamLeader().has_object_permission(make_request(plain_user), None, team) is True


def test_team_leader_denies_plain_member_of_target_team(make_request, plain_user, team):
    TeamMembership.objects.create(user=plain_user, team=team, role=TeamMembership.Role.MEMBER)
    assert IsTeamLeader().has_object_permission(make_request(plain_user), None, team) is False


def test_team_leader_denies_leader_of_a_different_team(make_request, plain_user, team):
    other = Team.objects.create(name="Beta")
    TeamMembership.objects.create(user=plain_user, team=other, role=TeamMembership.Role.LEADER)
    assert IsTeamLeader().has_object_permission(make_request(plain_user), None, team) is False


def test_team_leader_denies_non_member(make_request, plain_user, team):
    assert IsTeamLeader().has_object_permission(make_request(plain_user), None, team) is False


def test_team_leader_resolves_team_from_object_with_team_attr(make_request, plain_user, team):
    membership = TeamMembership.objects.create(
        user=plain_user, team=team, role=TeamMembership.Role.LEADER
    )
    assert IsTeamLeader().has_object_permission(make_request(plain_user), None, membership) is True


# --- IsTeamMember ---


def test_team_member_allows_plain_member(make_request, plain_user, team):
    TeamMembership.objects.create(user=plain_user, team=team, role=TeamMembership.Role.MEMBER)
    assert IsTeamMember().has_object_permission(make_request(plain_user), None, team) is True


def test_team_member_allows_leader(make_request, plain_user, team):
    TeamMembership.objects.create(user=plain_user, team=team, role=TeamMembership.Role.LEADER)
    assert IsTeamMember().has_object_permission(make_request(plain_user), None, team) is True


def test_team_member_denies_non_member(make_request, plain_user, team):
    assert IsTeamMember().has_object_permission(make_request(plain_user), None, team) is False
