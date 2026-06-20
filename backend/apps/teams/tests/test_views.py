import pytest
from django.urls import reverse

from apps.teams.models import Team, TeamMembership

pytestmark = pytest.mark.django_db


# --- Team CRUD ---


def test_admin_creates_team_and_becomes_leader(admin_client, admin_user, department):
    res = admin_client.post(
        reverse("team-list"),
        {"name": "Engineering", "description": "Eng", "department": department.id},
        format="json",
    )
    assert res.status_code == 201
    team = Team.objects.get(name="Engineering")
    membership = TeamMembership.objects.get(user=admin_user, team=team)
    assert membership.role == TeamMembership.Role.LEADER


def test_create_team_requires_department(admin_client):
    res = admin_client.post(reverse("team-list"), {"name": "NoDept"}, format="json")
    assert res.status_code == 400
    assert "department" in res.data


def test_create_team_requires_admin(member_client):
    res = member_client.post(reverse("team-list"), {"name": "X"}, format="json")
    assert res.status_code == 403


def test_create_team_requires_auth(api_client):
    res = api_client.post(reverse("team-list"), {"name": "X"}, format="json")
    assert res.status_code == 401


def test_duplicate_team_name_returns_400(admin_client, team):
    res = admin_client.post(reverse("team-list"), {"name": team.name}, format="json")
    assert res.status_code == 400
    assert "name" in res.data


def test_admin_lists_teams(admin_client, team):
    res = admin_client.get(reverse("team-list"))
    assert res.status_code == 200
    assert team.name in [t["name"] for t in res.data]


def test_admin_retrieves_team(admin_client, team):
    res = admin_client.get(reverse("team-detail", args=[team.id]))
    assert res.status_code == 200
    assert res.data["name"] == team.name


def test_admin_updates_team(admin_client, team):
    res = admin_client.patch(
        reverse("team-detail", args=[team.id]), {"description": "new"}, format="json"
    )
    assert res.status_code == 200
    team.refresh_from_db()
    assert team.description == "new"


def test_admin_deletes_team(admin_client, team):
    res = admin_client.delete(reverse("team-detail", args=[team.id]))
    assert res.status_code == 204
    assert not Team.objects.filter(id=team.id).exists()


def test_member_cannot_delete_team(member_client, team):
    res = member_client.delete(reverse("team-detail", args=[team.id]))
    assert res.status_code == 403


# --- Member management ---


def test_admin_adds_member_with_role(admin_client, team, member_user):
    res = admin_client.post(
        reverse("team-member-add", args=[team.id]),
        {"user": member_user.id, "role": "member"},
        format="json",
    )
    assert res.status_code == 201
    assert TeamMembership.objects.filter(user=member_user, team=team, role="member").exists()


def test_add_member_invalid_role_returns_400(admin_client, team, member_user):
    res = admin_client.post(
        reverse("team-member-add", args=[team.id]),
        {"user": member_user.id, "role": "boss"},
        format="json",
    )
    assert res.status_code == 400
    assert "role" in res.data


def test_add_duplicate_member_returns_400(admin_client, team, member_user):
    TeamMembership.objects.create(user=member_user, team=team, role=TeamMembership.Role.MEMBER)
    res = admin_client.post(
        reverse("team-member-add", args=[team.id]),
        {"user": member_user.id, "role": "leader"},
        format="json",
    )
    assert res.status_code == 400


def test_add_member_to_missing_team_returns_404(admin_client, member_user):
    res = admin_client.post(
        reverse("team-member-add", args=[9999]),
        {"user": member_user.id, "role": "member"},
        format="json",
    )
    assert res.status_code == 404


def test_admin_changes_member_role(admin_client, team, member_user):
    TeamMembership.objects.create(user=member_user, team=team, role=TeamMembership.Role.MEMBER)
    res = admin_client.patch(
        reverse("team-member-detail", args=[team.id, member_user.id]),
        {"role": "leader"},
        format="json",
    )
    assert res.status_code == 200
    membership = TeamMembership.objects.get(user=member_user, team=team)
    assert membership.role == TeamMembership.Role.LEADER


def test_admin_removes_member(admin_client, team, member_user):
    TeamMembership.objects.create(user=member_user, team=team, role=TeamMembership.Role.MEMBER)
    res = admin_client.delete(reverse("team-member-detail", args=[team.id, member_user.id]))
    assert res.status_code == 204
    assert not TeamMembership.objects.filter(user=member_user, team=team).exists()


def test_remove_nonexistent_member_returns_404(admin_client, team, member_user):
    res = admin_client.delete(reverse("team-member-detail", args=[team.id, member_user.id]))
    assert res.status_code == 404


def test_member_cannot_add_member(member_client, team, admin_user):
    res = member_client.post(
        reverse("team-member-add", args=[team.id]),
        {"user": admin_user.id, "role": "member"},
        format="json",
    )
    assert res.status_code == 403


def test_member_cannot_change_member_role(member_client, team, member_user):
    TeamMembership.objects.create(user=member_user, team=team, role=TeamMembership.Role.MEMBER)
    res = member_client.patch(
        reverse("team-member-detail", args=[team.id, member_user.id]),
        {"role": "leader"},
        format="json",
    )
    assert res.status_code == 403


def test_member_cannot_remove_member(member_client, team, member_user):
    TeamMembership.objects.create(user=member_user, team=team, role=TeamMembership.Role.MEMBER)
    res = member_client.delete(reverse("team-member-detail", args=[team.id, member_user.id]))
    assert res.status_code == 403


def test_member_detail_requires_auth(api_client, team, member_user):
    TeamMembership.objects.create(user=member_user, team=team, role=TeamMembership.Role.MEMBER)
    res = api_client.delete(reverse("team-member-detail", args=[team.id, member_user.id]))
    assert res.status_code == 401
