import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.teams.models import Department, Team, TeamMembership

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def department(db):
    return Department.objects.create(name="Engineering")


@pytest.fixture
def team(db, department):
    return Team.objects.create(name="Platform", department=department)


@pytest.fixture
def other_team(db, department):
    return Team.objects.create(name="Beta", department=department)


@pytest.fixture
def admin_user(db):
    return User.objects.create_user(
        email="admin@example.com", username="admin", password="Str0ng!Passw0rd", is_admin=True
    )


@pytest.fixture
def creator(db):
    return User.objects.create_user(
        email="creator@example.com", username="creator", password="Str0ng!Passw0rd"
    )


@pytest.fixture
def member_user(db):
    return User.objects.create_user(
        email="member@example.com", username="member", password="Str0ng!Passw0rd"
    )


@pytest.fixture
def leader_user(db):
    return User.objects.create_user(
        email="leader@example.com", username="leader", password="Str0ng!Passw0rd"
    )


@pytest.fixture
def outsider_user(db):
    return User.objects.create_user(
        email="outsider@example.com", username="outsider", password="Str0ng!Passw0rd"
    )


@pytest.fixture
def team_member(team, member_user):
    TeamMembership.objects.create(user=member_user, team=team, role=TeamMembership.Role.MEMBER)
    return member_user


@pytest.fixture
def team_leader(team, leader_user):
    TeamMembership.objects.create(user=leader_user, team=team, role=TeamMembership.Role.LEADER)
    return leader_user


@pytest.fixture
def dept_lead(db, department):
    user = User.objects.create_user(
        email="deptlead@example.com", username="deptlead", password="Str0ng!Passw0rd"
    )
    department.lead = user
    department.save()
    return user


@pytest.fixture
def dept_lead_client(api_client, dept_lead):
    api_client.force_authenticate(user=dept_lead)
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def creator_client(api_client, creator):
    api_client.force_authenticate(user=creator)
    return api_client


@pytest.fixture
def member_client(api_client, team_member):
    api_client.force_authenticate(user=team_member)
    return api_client


@pytest.fixture
def leader_client(api_client, team_leader):
    api_client.force_authenticate(user=team_leader)
    return api_client


@pytest.fixture
def outsider_client(api_client, outsider_user):
    api_client.force_authenticate(user=outsider_user)
    return api_client
