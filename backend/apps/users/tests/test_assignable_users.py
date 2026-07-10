"""The assignee picker is fed by GET /users/. A lead must see the people they are
allowed to assign (README §5: their teams' members, their department's members),
not just admins. These lock the user-list scoping to that authority."""

import pytest
from django.contrib.auth import get_user_model

from apps.teams.models import Department, Team, TeamMembership

User = get_user_model()

pytestmark = pytest.mark.django_db


def _member(username, team, role=TeamMembership.Role.MEMBER):
    u = User.objects.create_user(
        email=f"{username}@example.com",
        username=username,
        password="Str0ng!Passw0rd",
        first_name=username.capitalize(),
        last_name="Nguyen",
    )
    TeamMembership.objects.create(user=u, team=team, role=role)
    return u


def test_team_leader_lists_own_team_members(api_client, user, user_list_url):
    dept = Department.objects.create(name="Dept")
    team = Team.objects.create(name="Team A", department=dept)
    TeamMembership.objects.create(user=user, team=team, role=TeamMembership.Role.LEADER)
    member = _member("teammate", team)
    outsider = _member("outsider", Team.objects.create(name="Team B", department=dept))

    api_client.force_authenticate(user=user)
    res = api_client.get(user_list_url)

    assert res.status_code == 200
    ids = {u["id"] for u in res.data}
    assert user.id in ids  # self, so the lead can still self-assign
    assert member.id in ids
    assert outsider.id not in ids


def test_department_lead_lists_department_members(api_client, user, user_list_url):
    dept = Department.objects.create(name="Owned", lead=user)
    member = _member("deptmember", Team.objects.create(name="Team A", department=dept))
    other_dept = Department.objects.create(name="Other")
    outsider = _member("outsider", Team.objects.create(name="Team B", department=other_dept))

    api_client.force_authenticate(user=user)
    res = api_client.get(user_list_url)

    assert res.status_code == 200
    ids = {u["id"] for u in res.data}
    assert member.id in ids
    assert outsider.id not in ids


def test_plain_member_cannot_list_users(auth_client, user, user_list_url):
    team = Team.objects.create(name="Team A", department=Department.objects.create(name="Dept"))
    TeamMembership.objects.create(user=user, team=team, role=TeamMembership.Role.MEMBER)

    res = auth_client.get(user_list_url)

    assert res.status_code == 403


def test_admin_still_lists_everyone(admin_client, admin_user, user, user_list_url):
    res = admin_client.get(user_list_url)

    assert res.status_code == 200
    ids = {u["id"] for u in res.data}
    assert {admin_user.id, user.id} <= ids
