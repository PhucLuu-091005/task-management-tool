from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from django.core.management import call_command

from apps.tasks.models import Task

pytestmark = pytest.mark.django_db

VN = ZoneInfo("Asia/Ho_Chi_Minh")


def test_command_emails_overdue_assignee(creator, recipient, mailoutbox):
    Task.objects.create(
        title="Overdue",
        created_by=creator,
        assignee_type=Task.AssigneeType.USER,
        assignee_user=recipient,
        status=Task.Status.OVERDUE,
        due_date=datetime(2026, 7, 1, 9, 0, tzinfo=VN),
    )
    call_command("send_task_reminders")
    assert [m.to for m in mailoutbox] == [[recipient.email]]
