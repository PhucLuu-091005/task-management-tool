from datetime import timedelta

import pytest
from django.db.models import ProtectedError
from django.utils import timezone

from apps.tasks.models import Task, TaskStatusEvent


@pytest.mark.django_db
def test_task_str_returns_title(creator, team):
    task = Task.objects.create(
        title="Ship it",
        created_by=creator,
        assignee_type=Task.AssigneeType.TEAM,
        assignee_team=team,
    )
    assert str(task) == "Ship it"


@pytest.mark.django_db
def test_default_status_is_new(creator, member_user):
    task = Task.objects.create(
        title="T",
        created_by=creator,
        assignee_type=Task.AssigneeType.USER,
        assignee_user=member_user,
    )
    assert task.status == Task.Status.NEW


@pytest.mark.django_db
def test_is_overdue_true_when_past_due_and_not_done(creator, member_user):
    task = Task.objects.create(
        title="Late",
        created_by=creator,
        assignee_type=Task.AssigneeType.USER,
        assignee_user=member_user,
        due_date=timezone.now() - timedelta(hours=1),
    )
    assert task.is_overdue is True


@pytest.mark.django_db
def test_is_overdue_false_when_done(creator, member_user):
    task = Task.objects.create(
        title="Done late",
        created_by=creator,
        assignee_type=Task.AssigneeType.USER,
        assignee_user=member_user,
        status=Task.Status.DONE,
        due_date=timezone.now() - timedelta(hours=1),
    )
    assert task.is_overdue is False


@pytest.mark.django_db
def test_is_overdue_false_when_no_due_date(creator, member_user):
    task = Task.objects.create(
        title="No deadline",
        created_by=creator,
        assignee_type=Task.AssigneeType.USER,
        assignee_user=member_user,
    )
    assert task.is_overdue is False


@pytest.mark.django_db
def test_creator_is_protected_from_delete(creator, member_user):
    # created_by is PROTECT: authorship is a historical fact, so a user with tasks can't be deleted.
    Task.objects.create(
        title="Owned",
        created_by=creator,
        assignee_type=Task.AssigneeType.USER,
        assignee_user=member_user,
    )
    with pytest.raises(ProtectedError):
        creator.delete()


@pytest.mark.django_db
def test_deleting_assignee_nulls_the_assignment(creator, member_user):
    # assignee_* is SET_NULL: an assignment is reassignable, so the task survives unassigned.
    task = Task.objects.create(
        title="Assigned",
        created_by=creator,
        assignee_type=Task.AssigneeType.USER,
        assignee_user=member_user,
    )
    member_user.delete()
    task.refresh_from_db()
    assert task.assignee_user_id is None


S = Task.Status


@pytest.mark.django_db
def test_assigned_at_defaults_to_none(creator, member_user):
    task = Task.objects.create(
        title="T",
        created_by=creator,
        assignee_type=Task.AssigneeType.USER,
        assignee_user=member_user,
    )
    assert task.assigned_at is None


@pytest.mark.django_db
def test_status_events_ordered_chronologically(creator, member_user):
    task = Task.objects.create(
        title="T",
        created_by=creator,
        assignee_type=Task.AssigneeType.USER,
        assignee_user=member_user,
    )
    first = TaskStatusEvent.objects.create(
        task=task, from_status=S.NEW, to_status=S.IN_PROGRESS, changed_by=creator
    )
    second = TaskStatusEvent.objects.create(
        task=task, from_status=S.IN_PROGRESS, to_status=S.DONE, changed_by=creator
    )
    assert list(task.status_events.all()) == [first, second]
    assert first.changed_at is not None


@pytest.mark.django_db
def test_status_event_allows_system_change(creator, member_user):
    task = Task.objects.create(
        title="T",
        created_by=creator,
        assignee_type=Task.AssigneeType.USER,
        assignee_user=member_user,
    )
    event = TaskStatusEvent.objects.create(
        task=task, from_status=S.NEW, to_status=S.OVERDUE, changed_by=None
    )
    assert event.changed_by is None


@pytest.mark.parametrize(
    "from_status,to_status",
    [
        (S.NEW, S.IN_PROGRESS),
        (S.IN_PROGRESS, S.DONE),
        (S.OVERDUE, S.IN_PROGRESS),
        (S.OVERDUE, S.DONE),
    ],
)
def test_can_transition_allows_valid_moves(from_status, to_status):
    assert Task.can_transition(from_status, to_status) is True


@pytest.mark.parametrize(
    "from_status,to_status",
    [
        (S.NEW, S.DONE),  # must pass through in_progress
        (S.IN_PROGRESS, S.NEW),  # revert not allowed
        (S.DONE, S.IN_PROGRESS),  # reopen not allowed
        (S.DONE, S.NEW),  # done is terminal
        (S.OVERDUE, S.NEW),  # overdue never rewinds to new
        (S.NEW, S.NEW),  # same-status is not a transition
        (S.IN_PROGRESS, S.IN_PROGRESS),
        (S.NEW, S.OVERDUE),  # overdue is system-managed, never a manual target
        (S.IN_PROGRESS, S.OVERDUE),
    ],
)
def test_can_transition_rejects_invalid_moves(from_status, to_status):
    assert Task.can_transition(from_status, to_status) is False
