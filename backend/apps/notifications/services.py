import logging
import threading
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone

from apps.notifications import constants
from apps.tasks.models import Task
from apps.teams.models import TeamMembership

logger = logging.getLogger(__name__)

REMINDER_TZ = ZoneInfo("Asia/Ho_Chi_Minh")


def _local_day_bounds(now: datetime) -> tuple[datetime, datetime]:
    local = now.astimezone(REMINDER_TZ)
    start = datetime.combine(local.date(), time.min, tzinfo=REMINDER_TZ)
    return start, start + timedelta(days=1)


def build_reminder_digests(now: datetime | None = None) -> dict:
    now = now or timezone.now()
    start, end = _local_day_bounds(now)
    buckets = (
        (
            "due_today",
            Task.objects.filter(
                status__in=[Task.Status.NEW, Task.Status.IN_PROGRESS],
                due_date__gte=start,
                due_date__lt=end,
            ),
        ),
        ("overdue", Task.objects.filter(status=Task.Status.OVERDUE)),
    )
    digests: dict = {}
    for name, qs in buckets:
        for task in qs:
            for user in recipients_for_assignment(task):
                if user is None or not user.email:
                    continue
                digests.setdefault(user, {"due_today": [], "overdue": []})[name].append(task)
    return digests


def _task_url(task):
    return f"{settings.FRONTEND_URL}{constants.TASK_DETAIL_PATH.format(id=task.id)}"


def send_task_reminders(now=None) -> int:
    sent = 0
    for user, buckets in build_reminder_digests(now).items():
        body = render_to_string(
            constants.TASK_REMINDER_TEMPLATE,
            {
                "due_today": [
                    {"title": t.title, "url": _task_url(t)} for t in buckets["due_today"]
                ],
                "overdue": [{"title": t.title, "url": _task_url(t)} for t in buckets["overdue"]],
            },
        )
        try:
            send_mail(
                constants.TASK_REMINDER_SUBJECT, body, settings.DEFAULT_FROM_EMAIL, [user.email]
            )
            sent += 1
        except Exception:
            logger.exception("Failed to send task-reminder email to %s", user.email)
    return sent


def recipients_for_assignment(task):
    if task.assignee_type == Task.AssigneeType.USER:
        return [task.assignee_user] if task.assignee_user_id else []
    if task.assignee_type == Task.AssigneeType.TEAM:
        if not task.assignee_team_id:
            return []
        leader_ids = TeamMembership.objects.filter(
            team_id=task.assignee_team_id, role=TeamMembership.Role.LEADER
        ).values_list("user_id", flat=True)
        return list(get_user_model().objects.filter(id__in=leader_ids))
    if task.assignee_type == Task.AssigneeType.DEPARTMENT:
        if task.assignee_department_id and task.assignee_department.lead_id:
            return [task.assignee_department.lead]
        return []
    return []


def _recipient_emails(task, actor) -> list[str]:
    actor_id = actor.id if actor is not None else None
    seen: set[int] = set()
    emails = []
    for user in recipients_for_assignment(task):
        if user is None or user.id == actor_id or user.id in seen or not user.email:
            continue
        seen.add(user.id)
        emails.append(user.email)
    return emails


def notify_task_assignment(task, actor=None) -> int:
    emails = _recipient_emails(task, actor)
    if not emails:
        return 0
    subject = constants.TASK_ASSIGNED_SUBJECT.format(title=task.title)
    task_url = f"{settings.FRONTEND_URL}{constants.TASK_DETAIL_PATH.format(id=task.id)}"
    # Subject/body are rendered here so the worker thread never touches the DB —
    # the task row is already committed (no ATOMIC_REQUESTS).
    body = render_to_string(
        constants.TASK_ASSIGNED_TEMPLATE,
        {
            "task_title": task.title,
            "task_description": task.description,
            "task_url": task_url,
        },
    )
    _dispatch(_send_assignment_email, subject, body, emails)
    return len(emails)


def _dispatch(target, *args) -> None:
    threading.Thread(target=target, args=args, daemon=True).start()


def _send_assignment_email(subject, body, recipients) -> None:
    for email in recipients:
        try:
            send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [email])
        except Exception:
            logger.exception("Failed to send task-assignment email to %s", email)
