from datetime import timedelta

import pytest
from django.core.management import call_command
from django.utils import timezone

from apps.tasks.models import Task

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
