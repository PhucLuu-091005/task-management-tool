import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.tasks.models import Task

User = get_user_model()

pytestmark = pytest.mark.django_db


def _detail(task):
    return reverse("task-detail", args=[task.id])


def test_team_task_exposes_team_name(member_client, team, creator):
    task = Task.objects.create(
        title="Task",
        created_by=creator,
        assignee_type=Task.AssigneeType.TEAM,
        assignee_team=team,
    )

    res = member_client.get(_detail(task))

    assert res.status_code == 200
    assert res.data["assignee_team_name"] == team.name
    assert res.data["assignee_user_name"] is None
    assert res.data["assignee_department_name"] is None


def test_department_task_exposes_department_name(admin_client, department, creator):
    task = Task.objects.create(
        title="Task",
        created_by=creator,
        assignee_type=Task.AssigneeType.DEPARTMENT,
        assignee_department=department,
    )

    res = admin_client.get(_detail(task))

    assert res.data["assignee_department_name"] == department.name


def test_user_task_exposes_user_display_name(creator_client, creator):
    assignee = User.objects.create_user(
        email="phuc@example.com",
        username="phuc",
        password="Str0ng!Passw0rd",
        first_name="Phúc",
        last_name="Lưu",
    )
    task = Task.objects.create(
        title="Task",
        created_by=creator,
        assignee_type=Task.AssigneeType.USER,
        assignee_user=assignee,
    )

    res = creator_client.get(_detail(task))

    assert res.data["assignee_user_name"] == "Lưu Phúc"


def test_user_display_name_falls_back_to_username(creator_client, creator, member_user):
    task = Task.objects.create(
        title="Task",
        created_by=creator,
        assignee_type=Task.AssigneeType.USER,
        assignee_user=member_user,
    )

    res = creator_client.get(_detail(task))

    assert res.data["assignee_user_name"] == member_user.username


def test_created_by_name_is_exposed(creator_client, team, creator):
    task = Task.objects.create(
        title="Task",
        created_by=creator,
        assignee_type=Task.AssigneeType.TEAM,
        assignee_team=team,
    )

    res = creator_client.get(_detail(task))

    assert res.data["created_by_name"] == creator.username


def test_list_includes_display_names(member_client, team, creator):
    Task.objects.create(
        title="Task",
        created_by=creator,
        assignee_type=Task.AssigneeType.TEAM,
        assignee_team=team,
    )

    res = member_client.get(reverse("task-list"))

    assert res.status_code == 200
    row = res.data["results"][0]
    assert row["assignee_team_name"] == team.name
    assert row["created_by_name"] == creator.username
