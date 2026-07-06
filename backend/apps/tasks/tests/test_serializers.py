from types import SimpleNamespace

import pytest

from apps.tasks.constants import (
    ASSIGNEE_REQUIRED_ERROR_MESSAGE,
    INVALID_STATUS_TRANSITION_ERROR_MESSAGE,
)
from apps.tasks.models import Task
from apps.tasks.serializers import TaskSerializer, TaskStatusSerializer

pytestmark = pytest.mark.django_db


def _task(creator, member_user, status=Task.Status.NEW):
    return Task.objects.create(
        title="T",
        created_by=creator,
        assignee_type=Task.AssigneeType.USER,
        assignee_user=member_user,
        status=status,
    )


def test_valid_user_assignment(member_user):
    s = TaskSerializer(
        data={"title": "T", "assignee_type": "user", "assignee_user": member_user.id}
    )
    assert s.is_valid(), s.errors


def test_valid_team_assignment(team):
    s = TaskSerializer(data={"title": "T", "assignee_type": "team", "assignee_team": team.id})
    assert s.is_valid(), s.errors


def test_valid_department_assignment(department):
    s = TaskSerializer(
        data={"title": "T", "assignee_type": "department", "assignee_department": department.id}
    )
    assert s.is_valid(), s.errors


def test_missing_matching_assignee_is_invalid(team):
    s = TaskSerializer(data={"title": "T", "assignee_type": "user", "assignee_team": team.id})
    assert not s.is_valid()
    assert ASSIGNEE_REQUIRED_ERROR_MESSAGE.format(type="user") in str(s.errors)


def test_missing_assignee_type_is_invalid_not_500():
    s = TaskSerializer(data={"title": "T"})
    assert s.is_valid() is False
    assert "assignee_type" in s.errors


def test_extra_assignee_is_invalid(member_user, team):
    s = TaskSerializer(
        data={
            "title": "T",
            "assignee_type": "user",
            "assignee_user": member_user.id,
            "assignee_team": team.id,
        }
    )
    assert not s.is_valid()


def test_status_and_created_by_are_read_only():
    s = TaskSerializer()
    assert s.fields["status"].read_only
    assert s.fields["created_by"].read_only
    assert s.fields["is_overdue"].read_only


@pytest.mark.parametrize(
    "from_status,to_status",
    [
        (Task.Status.NEW, Task.Status.IN_PROGRESS),
        (Task.Status.IN_PROGRESS, Task.Status.DONE),
        (Task.Status.OVERDUE, Task.Status.IN_PROGRESS),
        (Task.Status.OVERDUE, Task.Status.DONE),
    ],
)
def test_status_serializer_accepts_valid_transition(creator, member_user, from_status, to_status):
    task = _task(creator, member_user, status=from_status)
    s = TaskStatusSerializer(task, data={"status": to_status})
    assert s.is_valid(), s.errors


@pytest.mark.parametrize(
    "from_status,to_status",
    [
        (Task.Status.NEW, Task.Status.DONE),
        (Task.Status.IN_PROGRESS, Task.Status.NEW),
        (Task.Status.DONE, Task.Status.IN_PROGRESS),
        (Task.Status.NEW, Task.Status.NEW),
    ],
)
def test_status_serializer_rejects_invalid_transition(creator, member_user, from_status, to_status):
    task = _task(creator, member_user, status=from_status)
    s = TaskStatusSerializer(task, data={"status": to_status})
    assert not s.is_valid()
    assert "status" in s.errors
    assert INVALID_STATUS_TRANSITION_ERROR_MESSAGE.format(
        from_status=from_status, to_status=to_status
    ) in str(s.errors)


def test_status_serializer_rejects_overdue_target(creator, member_user):
    task = _task(creator, member_user, status=Task.Status.NEW)
    s = TaskStatusSerializer(task, data={"status": "overdue"})
    assert not s.is_valid()
    assert "status" in s.errors


def test_status_update_does_not_clobber_concurrent_field_edit(creator, member_user):
    task = _task(creator, member_user, status=Task.Status.NEW)
    s = TaskStatusSerializer(
        task,
        data={"status": Task.Status.IN_PROGRESS},
        context={"request": SimpleNamespace(user=creator)},
    )
    assert s.is_valid(), s.errors
    # A concurrent request commits a title change after the instance was loaded
    # but before save(); the status write must not revert it to the stale snapshot.
    Task.objects.filter(pk=task.pk).update(title="concurrent edit")

    s.save()

    task.refresh_from_db()
    assert task.status == Task.Status.IN_PROGRESS
    assert task.title == "concurrent edit"
