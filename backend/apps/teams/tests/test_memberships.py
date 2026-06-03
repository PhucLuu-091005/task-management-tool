import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from apps.teams.models import Team, TeamMembership

User = get_user_model()

pytestmark = pytest.mark.django_db


@pytest.fixture
def team():
    return Team.objects.create(name="Team Alpha")


@pytest.fixture
def member_user():
    return User.objects.create_user(
        email="mai@example.com", username="mai", password="Str0ng!Passw0rd"
    )


def test_membership_role_choices_are_leader_member():
    assert set(TeamMembership.Role.values) == {"leader", "member"}


def test_membership_links_user_and_team_with_role(team, member_user):
    membership = TeamMembership.objects.create(
        user=member_user, team=team, role=TeamMembership.Role.LEADER
    )
    assert membership.user == member_user
    assert membership.team == team
    assert membership.role == "leader"


def test_user_can_lead_one_team_and_be_member_of_another(member_user):
    alpha = Team.objects.create(name="Alpha")
    beta = Team.objects.create(name="Beta")
    TeamMembership.objects.create(user=member_user, team=alpha, role=TeamMembership.Role.LEADER)
    TeamMembership.objects.create(user=member_user, team=beta, role=TeamMembership.Role.MEMBER)
    assert member_user.teams.count() == 2


def test_user_team_pair_is_unique(team, member_user):
    TeamMembership.objects.create(user=member_user, team=team, role=TeamMembership.Role.MEMBER)
    with pytest.raises(IntegrityError):
        TeamMembership.objects.create(user=member_user, team=team, role=TeamMembership.Role.LEADER)
