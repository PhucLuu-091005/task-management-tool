import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.tasks.models import Task
from apps.teams.models import Department, Team, TeamMembership

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def creator(db):
    return User.objects.create_user(
        email="creator@example.com", username="creator", password="Str0ng!Passw0rd"
    )


@pytest.fixture
def recipient(db):
    return User.objects.create_user(
        email="recipient@example.com", username="recipient", password="Str0ng!Passw0rd"
    )


@pytest.fixture
def other_user(db):
    return User.objects.create_user(
        email="other@example.com", username="other", password="Str0ng!Passw0rd"
    )


@pytest.fixture
def lead_user(db):
    return User.objects.create_user(
        email="lead@example.com", username="lead", password="Str0ng!Passw0rd"
    )


@pytest.fixture
def member_user(db):
    return User.objects.create_user(
        email="member@example.com", username="member", password="Str0ng!Passw0rd"
    )


@pytest.fixture
def department(db, lead_user):
    return Department.objects.create(name="Engineering", lead=lead_user)


@pytest.fixture
def team(db, department):
    return Team.objects.create(name="Platform", department=department)


@pytest.fixture
def team_leader(team, lead_user):
    TeamMembership.objects.create(user=lead_user, team=team, role=TeamMembership.Role.LEADER)
    return lead_user


@pytest.fixture
def team_member(team, member_user):
    TeamMembership.objects.create(user=member_user, team=team, role=TeamMembership.Role.MEMBER)
    return member_user


@pytest.fixture
def user_task(db, creator, recipient):
    return Task.objects.create(
        title="A task",
        created_by=creator,
        assignee_type=Task.AssigneeType.USER,
        assignee_user=recipient,
    )
