import pytest

from apps.notifications import services
from apps.notifications.services import notify_task_assignment, recipients_for_assignment
from apps.tasks.models import Task

pytestmark = pytest.mark.django_db


def _task(creator, **kwargs):
    return Task.objects.create(title="T", created_by=creator, **kwargs)


def test_user_assignment_emails_assignee(creator, recipient, mailoutbox):
    task = _task(creator, assignee_type=Task.AssigneeType.USER, assignee_user=recipient)
    count = notify_task_assignment(task, actor=creator)
    assert count == 1
    assert [m.to for m in mailoutbox] == [[recipient.email]]


def test_team_assignment_emails_only_leaders(creator, team, team_leader, team_member, mailoutbox):
    task = _task(creator, assignee_type=Task.AssigneeType.TEAM, assignee_team=team)
    notify_task_assignment(task, actor=creator)
    assert [m.to for m in mailoutbox] == [[team_leader.email]]  # leader yes, plain member no


def test_department_assignment_emails_lead(creator, department, lead_user, mailoutbox):
    task = _task(
        creator, assignee_type=Task.AssigneeType.DEPARTMENT, assignee_department=department
    )
    notify_task_assignment(task, actor=creator)
    assert [m.to for m in mailoutbox] == [[lead_user.email]]


def test_actor_is_not_emailed(recipient, mailoutbox):
    # recipient assigns a task to themselves -> no self-notification
    task = _task(recipient, assignee_type=Task.AssigneeType.USER, assignee_user=recipient)
    count = notify_task_assignment(task, actor=recipient)
    assert count == 0
    assert mailoutbox == []


def test_department_without_lead_emails_nobody(creator, department, mailoutbox):
    department.lead = None
    department.save()
    task = _task(
        creator, assignee_type=Task.AssigneeType.DEPARTMENT, assignee_department=department
    )
    assert notify_task_assignment(task, actor=creator) == 0
    assert mailoutbox == []


def test_recipients_for_team_returns_leaders(creator, team, team_leader):
    task = _task(creator, assignee_type=Task.AssigneeType.TEAM, assignee_team=team)
    assert list(recipients_for_assignment(task)) == [team_leader]


def test_team_with_multiple_leaders_emails_all(
    creator, team, team_leader, second_leader, mailoutbox
):
    task = _task(creator, assignee_type=Task.AssigneeType.TEAM, assignee_team=team)
    count = notify_task_assignment(task, actor=creator)
    assert count == 2
    assert sorted(m.to[0] for m in mailoutbox) == sorted([team_leader.email, second_leader.email])


def test_actor_leader_excluded_other_leader_emailed(team, team_leader, second_leader, mailoutbox):
    # a leader assigns to their own team: they are excluded, the co-leader still gets it
    task = _task(team_leader, assignee_type=Task.AssigneeType.TEAM, assignee_team=team)
    count = notify_task_assignment(task, actor=team_leader)
    assert count == 1
    assert [m.to for m in mailoutbox] == [[second_leader.email]]


def test_recipient_without_email_is_skipped(creator, recipient, mailoutbox):
    recipient.email = ""
    recipient.save()
    task = _task(creator, assignee_type=Task.AssigneeType.USER, assignee_user=recipient)
    assert notify_task_assignment(task, actor=creator) == 0
    assert mailoutbox == []


def test_send_failure_is_logged_not_raised(creator, recipient, mailoutbox, caplog, monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("smtp down")

    monkeypatch.setattr(services, "send_mail", boom)
    task = _task(creator, assignee_type=Task.AssigneeType.USER, assignee_user=recipient)
    notify_task_assignment(task, actor=creator)  # must not raise
    assert mailoutbox == []
    assert "Failed to send task-assignment email" in caplog.text
