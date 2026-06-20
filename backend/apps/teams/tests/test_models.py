import pytest
from django.db import IntegrityError

from apps.teams.models import Department, Team


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


@pytest.mark.django_db
def test_team_name_must_be_unique():
    Team.objects.create(name="Team Alpha")
    with pytest.raises(IntegrityError):
        Team.objects.create(name="Team Alpha")


@pytest.mark.django_db
def test_department_str_returns_name():
    dept = Department.objects.create(name="Engineering")
    assert str(dept) == "Engineering"


@pytest.mark.django_db
def test_department_name_is_unique():
    Department.objects.create(name="Engineering")
    with pytest.raises(IntegrityError):
        Department.objects.create(name="Engineering")


@pytest.mark.django_db
def test_department_lead_nulls_on_user_delete():
    from django.contrib.auth import get_user_model

    user = get_user_model().objects.create_user(
        email="lead@example.com", username="leadx", password="Str0ng!Passw0rd"
    )
    dept = Department.objects.create(name="Ops", lead=user)
    user.delete()
    dept.refresh_from_db()
    assert dept.lead is None
