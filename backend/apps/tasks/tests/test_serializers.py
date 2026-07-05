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
        (Task.Status.NEW, "in_progress"),
        (Task.Status.IN_PROGRESS, "done"),
        (Task.Status.OVERDUE, "in_progress"),
        (Task.Status.OVERDUE, "done"),
    ],
)
def test_status_serializer_accepts_valid_transition(creator, member_user, from_status, to_status):
    task = _task(creator, member_user, status=from_status)
    s = TaskStatusSerializer(task, data={"status": to_status})
    assert s.is_valid(), s.errors


@pytest.mark.parametrize(
    "from_status,to_status",
    [
        (Task.Status.NEW, "done"),
        (Task.Status.IN_PROGRESS, "new"),
        (Task.Status.DONE, "in_progress"),
        (Task.Status.NEW, "new"),
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
