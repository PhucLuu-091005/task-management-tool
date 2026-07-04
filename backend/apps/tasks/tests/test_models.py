from datetime import timedelta

import pytest
from django.db.models import ProtectedError
from django.utils import timezone

from apps.tasks.models import Task


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
