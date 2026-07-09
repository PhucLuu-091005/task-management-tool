import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from apps.teams.models import Department, Team, TeamMembership

User = get_user_model()


@pytest.mark.django_db
def test_str_return_email_not_username(user):
    assert str(user) == user.email
    assert str(user) != user.username


@pytest.mark.django_db
def test_email_must_be_unique(user):
    with pytest.raises(IntegrityError):
        User.objects.create_user(
            email=user.email,
            username="different_user",
            password="random123214@",
        )


@pytest.mark.django_db
def test_username_must_be_unique(user):
    with pytest.raises(IntegrityError):
        User.objects.create_user(
            email="different@email.com",
            username=user.username,
            password="random123214@",
        )


@pytest.mark.django_db
def test_full_name_must_be_unique(user):
    with pytest.raises(IntegrityError):
        User.objects.create_user(
            email="different@email.com",
            username="different_user",
            password="random123214@",
            first_name=user.first_name,
            last_name=user.last_name,
        )


@pytest.mark.django_db
def test_empty_full_name_can_repeat():
    # System/fixture accounts without a name are exempt from unique_full_name.
    User.objects.create_user(email="a@example.com", username="a", password="random123214@")
    User.objects.create_user(email="b@example.com", username="b", password="random123214@")
    assert User.objects.filter(first_name="", last_name="").count() == 2


# Global admin flag (A3)


@pytest.mark.django_db
def test_new_user_is_not_admin_by_default(user):
    assert user.is_admin is False


@pytest.mark.django_db
def test_with_memberships_prefetches_team(user, django_assert_num_queries):
    dept = Department.objects.create(name="Dept Models Alpha")
    team = Team.objects.create(name="Alpha", department=dept)
    TeamMembership.objects.create(user=user, team=team, role=TeamMembership.Role.MEMBER)

    fetched = User.objects.with_memberships().get(pk=user.pk)
    # team is prefetched + select_related, so reading team.name does no extra query
    with django_assert_num_queries(0):
        names = [m.team.name for m in fetched.memberships.all()]
    assert names == ["Alpha"]
