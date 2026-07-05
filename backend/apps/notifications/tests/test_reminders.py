from datetime import UTC, datetime
from zoneinfo import ZoneInfo

import pytest

from apps.notifications.services import build_reminder_digests
from apps.tasks.models import Task
from apps.teams.models import Team, TeamMembership

pytestmark = pytest.mark.django_db

from apps.notifications.services import send_task_reminders  # noqa: E402

VN = ZoneInfo("Asia/Ho_Chi_Minh")
# 2026-07-05 08:30 Asia/Ho_Chi_Minh == 01:30 UTC
NOW = datetime(2026, 7, 5, 1, 30, tzinfo=UTC)


def _task(creator, **kwargs):
    kwargs.setdefault("title", "T")
    return Task.objects.create(created_by=creator, **kwargs)


def test_due_today_task_for_user_assignee(creator, recipient):
    task = _task(
        creator,
        assignee_type=Task.AssigneeType.USER,
        assignee_user=recipient,
        status=Task.Status.NEW,
        due_date=datetime(2026, 7, 5, 17, 0, tzinfo=VN),
    )
    digests = build_reminder_digests(now=NOW)
    assert digests[recipient]["due_today"] == [task]
    assert digests[recipient]["overdue"] == []


def test_overdue_task_uses_stored_status(creator, recipient):
    task = _task(
        creator,
        assignee_type=Task.AssigneeType.USER,
        assignee_user=recipient,
        status=Task.Status.OVERDUE,
        due_date=datetime(2026, 7, 1, 12, 0, tzinfo=VN),
    )
    digests = build_reminder_digests(now=NOW)
    assert digests[recipient]["overdue"] == [task]
    assert digests[recipient]["due_today"] == []


def test_done_task_is_excluded(creator, recipient):
    _task(
        creator,
        assignee_type=Task.AssigneeType.USER,
        assignee_user=recipient,
        status=Task.Status.DONE,
        due_date=datetime(2026, 7, 5, 10, 0, tzinfo=VN),
    )
    assert build_reminder_digests(now=NOW) == {}


def test_late_evening_due_date_still_counts_as_today(creator, recipient):
    # 23:30 local is still "today" in Asia/Ho_Chi_Minh, not tomorrow.
    task = _task(
        creator,
        assignee_type=Task.AssigneeType.USER,
        assignee_user=recipient,
        status=Task.Status.IN_PROGRESS,
        due_date=datetime(2026, 7, 5, 23, 30, tzinfo=VN),
    )
    digests = build_reminder_digests(now=NOW)
    assert digests[recipient]["due_today"] == [task]


def test_tomorrow_due_date_is_not_today(creator, recipient):
    _task(
        creator,
        assignee_type=Task.AssigneeType.USER,
        assignee_user=recipient,
        status=Task.Status.NEW,
        due_date=datetime(2026, 7, 6, 0, 30, tzinfo=VN),
    )
    assert build_reminder_digests(now=NOW) == {}


def test_leader_of_two_teams_grouped_into_one_entry(creator, team, team_leader):
    second_team = Team.objects.create(name="Infra", department=team.department)
    TeamMembership.objects.create(
        user=team_leader, team=second_team, role=TeamMembership.Role.LEADER
    )
    t1 = _task(
        creator,
        assignee_type=Task.AssigneeType.TEAM,
        assignee_team=team,
        status=Task.Status.OVERDUE,
        due_date=datetime(2026, 7, 1, 9, 0, tzinfo=VN),
    )
    t2 = _task(
        creator,
        assignee_type=Task.AssigneeType.TEAM,
        assignee_team=second_team,
        status=Task.Status.OVERDUE,
        due_date=datetime(2026, 7, 2, 9, 0, tzinfo=VN),
    )
    digests = build_reminder_digests(now=NOW)
    assert list(digests.keys()) == [team_leader]
    assert set(digests[team_leader]["overdue"]) == {t1, t2}


def test_recipient_without_email_is_skipped(creator, team):
    leader = team.department.lead
    leader.email = ""
    leader.save()
    TeamMembership.objects.create(user=leader, team=team, role=TeamMembership.Role.LEADER)
    _task(
        creator,
        assignee_type=Task.AssigneeType.TEAM,
        assignee_team=team,
        status=Task.Status.OVERDUE,
        due_date=datetime(2026, 7, 1, 9, 0, tzinfo=VN),
    )
    assert build_reminder_digests(now=NOW) == {}


def test_sends_one_email_per_recipient_with_both_sections(settings, creator, recipient, mailoutbox):
    settings.FRONTEND_URL = "https://app.example.com"
    due = _task(
        creator,
        title="Due today task",
        assignee_type=Task.AssigneeType.USER,
        assignee_user=recipient,
        status=Task.Status.NEW,
        due_date=datetime(2026, 7, 5, 15, 0, tzinfo=VN),
    )
    late = _task(
        creator,
        title="Old overdue task",
        assignee_type=Task.AssigneeType.USER,
        assignee_user=recipient,
        status=Task.Status.OVERDUE,
        due_date=datetime(2026, 7, 1, 9, 0, tzinfo=VN),
    )
    sent = send_task_reminders(now=NOW)
    assert sent == 1
    assert [m.to for m in mailoutbox] == [[recipient.email]]
    body = mailoutbox[0].body
    assert due.title in body
    assert late.title in body
    assert f"https://app.example.com/tasks/{due.id}" in body


def test_no_tasks_sends_nothing(creator, mailoutbox):
    assert send_task_reminders(now=NOW) == 0
    assert mailoutbox == []
