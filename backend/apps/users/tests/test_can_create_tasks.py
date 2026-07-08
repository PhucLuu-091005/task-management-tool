import pytest

from apps.teams.models import Department, Team, TeamMembership

pytestmark = pytest.mark.django_db


def _team(name="T", dept_name="D"):
    dept = Department.objects.create(name=dept_name)
    return Team.objects.create(name=name, department=dept)


def test_user_with_no_roles_cannot_create(auth_client, profile_url):
    res = auth_client.get(profile_url)
    assert res.data["can_create_tasks"] is False


def test_plain_member_cannot_create(auth_client, profile_url, user):
    TeamMembership.objects.create(user=user, team=_team(), role=TeamMembership.Role.MEMBER)
    res = auth_client.get(profile_url)
    assert res.data["can_create_tasks"] is False


def test_team_leader_can_create(auth_client, profile_url, user):
    TeamMembership.objects.create(user=user, team=_team(), role=TeamMembership.Role.LEADER)
    res = auth_client.get(profile_url)
    assert res.data["can_create_tasks"] is True


def test_department_lead_can_create(auth_client, profile_url, user):
    # A department lead who is not a team leader must still count.
    Department.objects.create(name="Owned", lead=user)
    res = auth_client.get(profile_url)
    assert res.data["can_create_tasks"] is True


def test_admin_can_create(admin_client, profile_url):
    res = admin_client.get(profile_url)
    assert res.data["can_create_tasks"] is True
