import pytest
from django.contrib.auth import get_user_model

from apps.teams.models import Department, Team, TeamMembership

User = get_user_model()


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
def second_leader(team):
    user = User.objects.create_user(
        email="lead2@example.com", username="lead2", password="Str0ng!Passw0rd"
    )
    TeamMembership.objects.create(user=user, team=team, role=TeamMembership.Role.LEADER)
    return user
