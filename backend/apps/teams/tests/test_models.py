import pytest

from apps.teams.models import Team


@pytest.mark.django_db
def test_team_str_returns_name():
    team = Team.objects.create(name="Team Alpha")
    assert str(team) == "Team Alpha"


@pytest.mark.django_db
def test_team_created_with_optional_description():
    team = Team.objects.create(name="Team Beta", description="Backend squad")
    assert team.description == "Backend squad"


@pytest.mark.django_db
def test_team_has_timestamps():
    team = Team.objects.create(name="Team Gamma")
    assert team.created_at is not None
    assert team.updated_at is not None
