from datetime import timedelta
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.db.models import ProtectedError
from django.utils import timezone

from apps.tasks.models import Task

pytestmark = pytest.mark.django_db


def test_task_str_returns_title(team, creator):
    task = Task.objects.create(title="Ship the API", team=team, created_by=creator)
    assert str(task) == "Ship the API"


def test_minimal_task_persists_with_title_team_and_creator(team, creator):
    task = Task.objects.create(title="Write tests", team=team, created_by=creator)
    assert task.pk is not None
    assert task.title == "Write tests"
    assert task.team == team
    assert task.created_by == creator


def test_status_choices_are_the_five_lifecycle_values():
    assert set(Task.Status.values) == {
        "new",
        "in_progress",
        "in_review",
        "done",
        "rejected",
    }


def test_status_defaults_to_new(team, creator):
    task = Task.objects.create(title="Plan", team=team, created_by=creator)
    assert task.status == Task.Status.NEW


def test_priority_choices_run_none_to_urgent():
    assert set(Task.Priority.values) == {0, 1, 2, 3, 4}
    assert Task.Priority.NONE == 0
    assert Task.Priority.URGENT == 4


def test_priority_defaults_to_none(team, creator):
    task = Task.objects.create(title="No priority", team=team, created_by=creator)
    assert task.priority == Task.Priority.NONE


def test_description_defaults_to_blank(team, creator):
    task = Task.objects.create(title="No description", team=team, created_by=creator)
    assert task.description == ""


def test_estimate_hours_defaults_to_null(team, creator):
    task = Task.objects.create(title="Unestimated", team=team, created_by=creator)
    assert task.estimate_hours is None


def test_estimate_hours_accepts_decimal(team, creator):
    task = Task.objects.create(
        title="Estimated", team=team, created_by=creator, estimate_hours=Decimal("2.50")
    )
    task.refresh_from_db()
    assert task.estimate_hours == Decimal("2.50")


def test_estimate_hours_rejects_below_minimum(team, creator):
    task = Task(title="Too small", team=team, created_by=creator, estimate_hours=Decimal("0.00"))
    with pytest.raises(ValidationError):
        task.full_clean()


def test_assignee_is_optional(team, creator):
    task = Task.objects.create(title="Unassigned", team=team, created_by=creator)
    assert task.assignee is None


def test_due_date_is_optional(team, creator):
    task = Task.objects.create(title="No deadline", team=team, created_by=creator)
    assert task.due_date is None


def test_assignee_reverse_relation_resolves(team, creator, assignee):
    task = Task.objects.create(title="Assigned", team=team, created_by=creator, assignee=assignee)
    assert task.assignee == assignee
    assert task in assignee.assigned_tasks.all()


def test_created_by_reverse_relation_resolves(team, creator):
    task = Task.objects.create(title="Created", team=team, created_by=creator)
    assert task in creator.created_tasks.all()


def test_team_reverse_relation_resolves(team, creator):
    task = Task.objects.create(title="Owned", team=team, created_by=creator)
    assert task in team.tasks.all()


def test_deleting_assignee_keeps_task_and_nulls_assignee(team, creator, assignee):
    task = Task.objects.create(
        title="Keep on delete", team=team, created_by=creator, assignee=assignee
    )
    assignee.delete()
    task.refresh_from_db()
    assert task.assignee is None


def test_deleting_creator_is_blocked_by_protect(team, creator):
    Task.objects.create(title="Protected creator", team=team, created_by=creator)
    with pytest.raises(ProtectedError):
        creator.delete()


def test_deleting_team_cascades_to_tasks(team, creator):
    task = Task.objects.create(title="Cascade", team=team, created_by=creator)
    pk = task.pk
    team.delete()
    assert not Task.objects.filter(pk=pk).exists()


def test_task_has_timestamps(team, creator):
    task = Task.objects.create(title="Timestamped", team=team, created_by=creator)
    assert task.created_at is not None
    assert task.updated_at is not None


def test_tasks_ordered_by_newest_first(team, creator):
    first = Task.objects.create(title="First", team=team, created_by=creator)
    second = Task.objects.create(title="Second", team=team, created_by=creator)
    ordered = list(Task.objects.all())
    assert ordered.index(second) < ordered.index(first)


def test_is_overdue_true_for_past_due_and_not_done(team, creator):
    task = Task.objects.create(
        title="Late",
        team=team,
        created_by=creator,
        due_date=timezone.now() - timedelta(hours=1),
    )
    assert task.is_overdue is True


def test_is_overdue_false_when_due_in_future(team, creator):
    task = Task.objects.create(
        title="On time",
        team=team,
        created_by=creator,
        due_date=timezone.now() + timedelta(days=1),
    )
    assert task.is_overdue is False


def test_is_overdue_false_when_no_due_date(team, creator):
    task = Task.objects.create(title="No deadline", team=team, created_by=creator)
    assert task.is_overdue is False


def test_is_overdue_false_when_done_even_if_past_due(team, creator):
    task = Task.objects.create(
        title="Done late",
        team=team,
        created_by=creator,
        status=Task.Status.DONE,
        due_date=timezone.now() - timedelta(hours=1),
    )
    assert task.is_overdue is False
