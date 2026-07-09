import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.tasks.models import Task
from apps.teams.models import Department, Team

User = get_user_model()
pytestmark = pytest.mark.django_db


def _url(user_id):
    return reverse("user-detail", args=[user_id])


def test_admin_deletes_user(admin_client, user):
    res = admin_client.delete(_url(user.id))

    assert res.status_code == 204
    assert not User.objects.filter(id=user.id).exists()


def test_non_admin_cannot_delete(auth_client, admin_user):
    res = auth_client.delete(_url(admin_user.id))

    assert res.status_code == 403
    assert User.objects.filter(id=admin_user.id).exists()


def test_unauthenticated_cannot_delete(api_client, user):
    res = api_client.delete(_url(user.id))

    assert res.status_code == 401


def test_admin_cannot_delete_self(admin_client, admin_user):
    res = admin_client.delete(_url(admin_user.id))

    assert res.status_code == 400
    assert User.objects.filter(id=admin_user.id).exists()


def test_admin_cannot_delete_another_admin(admin_client):
    other_admin = User.objects.create_user(
        email="admin2@example.com",
        username="adminy",
        password="Str0ng!Passw0rd",
        first_name="Ad2",
        last_name="Min2",
        is_admin=True,
    )

    res = admin_client.delete(_url(other_admin.id))

    assert res.status_code == 403
    assert User.objects.filter(id=other_admin.id).exists()


def test_cannot_delete_user_who_created_tasks(admin_client, user):
    # Task.created_by is PROTECT, so deleting the creator must fail cleanly.
    dept = Department.objects.create(name="Dept Del")
    team = Team.objects.create(name="Team Del", department=dept)
    Task.objects.create(
        title="owned",
        assignee_type=Task.AssigneeType.TEAM,
        assignee_team=team,
        created_by=user,
    )

    res = admin_client.delete(_url(user.id))

    assert res.status_code == 409
    assert User.objects.filter(id=user.id).exists()


def test_cannot_delete_user_assigned_to_tasks(admin_client, admin_user, user):
    # A direct assignee is SET_NULL on delete, which would leave the task in an
    # invalid "type=user, assignee=null" state — block it instead.
    Task.objects.create(
        title="assigned",
        assignee_type=Task.AssigneeType.USER,
        assignee_user=user,
        created_by=admin_user,
    )

    res = admin_client.delete(_url(user.id))

    assert res.status_code == 409
    assert User.objects.filter(id=user.id).exists()
