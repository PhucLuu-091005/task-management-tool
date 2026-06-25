import pytest

from apps.notifications.models import Notification
from apps.notifications.services import notify_task_assignment, recipients_for_assignment
from apps.tasks.models import Task

pytestmark = pytest.mark.django_db


def _task(creator, **kwargs):
    return Task.objects.create(title="T", created_by=creator, **kwargs)


def test_user_assignment_notifies_assignee(creator, recipient):
    task = _task(creator, assignee_type=Task.AssigneeType.USER, assignee_user=recipient)
    count = notify_task_assignment(task, actor=creator)
    assert count == 1
    n = Notification.objects.get()
    assert n.recipient == recipient and n.task == task


def test_team_assignment_notifies_only_leaders(creator, team, team_leader, team_member):
    task = _task(creator, assignee_type=Task.AssigneeType.TEAM, assignee_team=team)
    notify_task_assignment(task, actor=creator)
    recipients = set(Notification.objects.values_list("recipient_id", flat=True))
    assert recipients == {team_leader.id}  # leader yes, plain member no


def test_department_assignment_notifies_lead(creator, department, lead_user):
    task = _task(
        creator, assignee_type=Task.AssigneeType.DEPARTMENT, assignee_department=department
    )
    notify_task_assignment(task, actor=creator)
    assert list(Notification.objects.values_list("recipient_id", flat=True)) == [lead_user.id]


def test_actor_is_not_notified(recipient):
    # recipient assigns a task to themselves -> no self-notification
    task = _task(recipient, assignee_type=Task.AssigneeType.USER, assignee_user=recipient)
    count = notify_task_assignment(task, actor=recipient)
    assert count == 0
    assert Notification.objects.count() == 0


def test_department_without_lead_notifies_nobody(creator, department):
    department.lead = None
    department.save()
    task = _task(
        creator, assignee_type=Task.AssigneeType.DEPARTMENT, assignee_department=department
    )
    assert notify_task_assignment(task, actor=creator) == 0


def test_recipients_for_team_returns_leaders(creator, team, team_leader):
    task = _task(creator, assignee_type=Task.AssigneeType.TEAM, assignee_team=team)
    assert list(recipients_for_assignment(task)) == [team_leader]
