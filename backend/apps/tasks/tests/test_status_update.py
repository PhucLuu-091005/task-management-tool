import pytest
from django.urls import reverse

from apps.tasks.models import Task

pytestmark = pytest.mark.django_db


def _team_task(creator, team):
    return Task.objects.create(
        title="Task",
        created_by=creator,
        assignee_type=Task.AssigneeType.TEAM,
        assignee_team=team,
    )


def _url(task):
    return reverse("task-status", args=[task.id])


def test_assigned_team_member_updates_status(member_client, team, creator):
    task = _team_task(creator, team)

    res = member_client.patch(_url(task), {"status": "in_progress"})

    assert res.status_code == 200
    task.refresh_from_db()
    assert task.status == Task.Status.IN_PROGRESS


def test_direct_user_assignee_updates_status(member_client, team_member, creator):
    task = Task.objects.create(
        title="Task",
        created_by=creator,
        assignee_type=Task.AssigneeType.USER,
        assignee_user=team_member,
    )

    res = member_client.patch(_url(task), {"status": "done"})

    assert res.status_code == 200
    task.refresh_from_db()
    assert task.status == Task.Status.DONE


def test_creator_updates_status(creator_client, team, creator):
    task = _team_task(creator, team)

    res = creator_client.patch(_url(task), {"status": "done"})

    assert res.status_code == 200


def test_response_is_full_task(member_client, team, creator):
    task = _team_task(creator, team)

    res = member_client.patch(_url(task), {"status": "in_progress"})

    assert res.data["id"] == task.id
    assert res.data["status"] == "in_progress"
    assert res.data["title"] == task.title
    assert "is_overdue" in res.data


def test_overdue_task_can_be_completed(member_client, team, creator):
    task = _team_task(creator, team)
    Task.objects.filter(id=task.id).update(status=Task.Status.OVERDUE)

    res = member_client.patch(_url(task), {"status": "done"})

    assert res.status_code == 200
    task.refresh_from_db()
    assert task.status == Task.Status.DONE


def test_cannot_set_overdue_manually(member_client, team, creator):
    task = _team_task(creator, team)

    res = member_client.patch(_url(task), {"status": "overdue"})

    assert res.status_code == 400
    assert "status" in res.data
    task.refresh_from_db()
    assert task.status == Task.Status.NEW


def test_invalid_status_is_rejected(member_client, team, creator):
    task = _team_task(creator, team)

    res = member_client.patch(_url(task), {"status": "finished"})

    assert res.status_code == 400
    assert "status" in res.data


def test_missing_status_is_rejected(member_client, team, creator):
    task = _team_task(creator, team)

    res = member_client.patch(_url(task), {})

    assert res.status_code == 400
    assert "status" in res.data


def test_hidden_task_is_404(member_client, other_team, creator):
    hidden = Task.objects.create(
        title="Task",
        created_by=creator,
        assignee_type=Task.AssigneeType.TEAM,
        assignee_team=other_team,
    )

    res = member_client.patch(_url(hidden), {"status": "done"})

    assert res.status_code == 404


def test_unauthenticated_cannot_update_status(api_client, team, creator):
    task = _team_task(creator, team)

    res = api_client.patch(_url(task), {"status": "done"})

    assert res.status_code in (401, 403)


def test_status_ignores_other_fields(member_client, team, creator):
    task = _team_task(creator, team)

    res = member_client.patch(_url(task), {"status": "done", "title": "hijacked"})

    assert res.status_code == 200
    task.refresh_from_db()
    assert task.title == "Task"
