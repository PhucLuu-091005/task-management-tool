from datetime import timedelta

import pytest
from django.core.management import call_command
from django.utils import timezone

from apps.tasks.models import Task, TaskStatusEvent

pytestmark = pytest.mark.django_db


def _task(creator, member_user, **kwargs):
    return Task.objects.create(
        title=kwargs.pop("title", "T"),
        created_by=creator,
        assignee_type=Task.AssigneeType.USER,
        assignee_user=member_user,
        **kwargs,
    )


def test_flips_past_due_new_task(creator, member_user):
    task = _task(creator, member_user, due_date=timezone.now() - timedelta(hours=1))
    call_command("flip_overdue_tasks")
    task.refresh_from_db()
    assert task.status == Task.Status.OVERDUE


def test_leaves_future_task(creator, member_user):
    task = _task(creator, member_user, due_date=timezone.now() + timedelta(hours=1))
    call_command("flip_overdue_tasks")
    task.refresh_from_db()
    assert task.status == Task.Status.NEW


def test_leaves_done_task(creator, member_user):
    task = _task(
        creator,
        member_user,
        status=Task.Status.DONE,
        due_date=timezone.now() - timedelta(hours=1),
    )
    call_command("flip_overdue_tasks")
    task.refresh_from_db()
    assert task.status == Task.Status.DONE


def test_flip_records_system_event(creator, member_user):
    task = _task(
        creator,
        member_user,
        status=Task.Status.IN_PROGRESS,
        due_date=timezone.now() - timedelta(hours=1),
    )
    call_command("flip_overdue_tasks")
    event = task.status_events.get()
    assert event.from_status == Task.Status.IN_PROGRESS
    assert event.to_status == Task.Status.OVERDUE
    assert event.changed_by is None


def test_flip_records_no_event_when_nothing_flips(creator, member_user):
    _task(creator, member_user, due_date=timezone.now() + timedelta(hours=1))
    call_command("flip_overdue_tasks")
    assert TaskStatusEvent.objects.count() == 0
