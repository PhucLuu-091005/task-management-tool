import pytest
from django.urls import reverse

from apps.tasks.models import Task

pytestmark = pytest.mark.django_db


def _task(creator, status, *, team=None, user=None, department=None):
    if team is not None:
        kind, field = Task.AssigneeType.TEAM, {"assignee_team": team}
    elif user is not None:
        kind, field = Task.AssigneeType.USER, {"assignee_user": user}
    else:
        kind, field = Task.AssigneeType.DEPARTMENT, {"assignee_department": department}
    return Task.objects.create(
        title="T", created_by=creator, status=status, assignee_type=kind, **field
    )


def test_stats_total_and_by_status(admin_client, creator, team, member_user, department):
    _task(creator, Task.Status.NEW, team=team)
    _task(creator, Task.Status.IN_PROGRESS, team=team)
    _task(creator, Task.Status.DONE, user=member_user)
    _task(creator, Task.Status.OVERDUE, department=department)

    res = admin_client.get(reverse("task-stats"))

    assert res.status_code == 200
    assert res.data["total"] == 4
    assert res.data["by_status"] == {
        "new": 1,
        "in_progress": 1,
        "done": 1,
        "overdue": 1,
    }


def test_stats_by_status_is_zero_filled(admin_client, creator, team):
    _task(creator, Task.Status.NEW, team=team)

    res = admin_client.get(reverse("task-stats"))

    assert res.data["by_status"] == {
        "new": 1,
        "in_progress": 0,
        "done": 0,
        "overdue": 0,
    }


def test_stats_groups_by_polymorphic_assignee(admin_client, creator, team, member_user, department):
    _task(creator, Task.Status.NEW, team=team)
    _task(creator, Task.Status.NEW, team=team)
    _task(creator, Task.Status.NEW, user=member_user)
    _task(creator, Task.Status.NEW, department=department)

    res = admin_client.get(reverse("task-stats"))

    assert res.data["by_team"] == [{"assignee_team_id": team.id, "count": 2}]
    assert res.data["by_assignee_user"] == [{"assignee_user_id": member_user.id, "count": 1}]
    assert res.data["by_department"] == [{"assignee_department_id": department.id, "count": 1}]


def test_stats_scoped_to_visibility(member_client, creator, team, other_team):
    _task(creator, Task.Status.NEW, team=team)
    _task(creator, Task.Status.NEW, team=other_team)

    res = member_client.get(reverse("task-stats"))

    assert res.status_code == 200
    assert res.data["total"] == 1
    assert res.data["by_status"]["new"] == 1


def test_stats_requires_authentication(api_client):
    res = api_client.get(reverse("task-stats"))

    assert res.status_code in (401, 403)
