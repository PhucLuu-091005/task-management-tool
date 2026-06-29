from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from apps.tasks.models import Task

pytestmark = pytest.mark.django_db


def _team_task(creator, team, **kwargs):
    return Task.objects.create(
        title=kwargs.pop("title", "Task"),
        created_by=creator,
        assignee_type=Task.AssigneeType.TEAM,
        assignee_team=team,
        **kwargs,
    )


def test_list_is_paginated(admin_client, creator, team):
    _team_task(creator, team, title="A")
    _team_task(creator, team, title="B")

    res = admin_client.get(reverse("task-list"))

    assert res.status_code == 200
    assert res.data["count"] == 2
    assert {t["title"] for t in res.data["results"]} == {"A", "B"}


def test_filter_by_priority(admin_client, creator, team):
    _team_task(creator, team, title="urgent", priority=Task.Priority.HIGH)
    _team_task(creator, team, title="meh", priority=Task.Priority.LOW)

    res = admin_client.get(reverse("task-list"), {"priority": Task.Priority.HIGH})

    assert [t["title"] for t in res.data["results"]] == ["urgent"]


def test_filter_by_is_overdue(admin_client, creator, team):
    past = timezone.now() - timedelta(days=1)
    _team_task(creator, team, title="late", status=Task.Status.NEW, due_date=past)
    _team_task(creator, team, title="closed", status=Task.Status.DONE, due_date=past)

    res = admin_client.get(reverse("task-list"), {"is_overdue": "true"})

    assert [t["title"] for t in res.data["results"]] == ["late"]


def test_search_matches_description(admin_client, creator, team):
    _team_task(creator, team, title="Ticket", description="kubernetes rollout plan")
    _team_task(creator, team, title="Other", description="nothing relevant")

    res = admin_client.get(reverse("task-list"), {"search": "kubernetes"})

    assert [t["title"] for t in res.data["results"]] == ["Ticket"]


def test_invalid_choice_filter_returns_400(admin_client):
    res = admin_client.get(reverse("task-list"), {"priority": "bogus"})

    assert res.status_code == 400


def test_pagination_paginates_beyond_one_page(admin_client, creator, team):
    for i in range(25):
        _team_task(creator, team, title=f"T{i:02d}")

    page1 = admin_client.get(reverse("task-list"))
    assert page1.data["count"] == 25
    assert len(page1.data["results"]) == 20
    assert page1.data["next"] is not None

    page2 = admin_client.get(reverse("task-list"), {"page": 2})
    assert len(page2.data["results"]) == 5


def test_other_list_endpoints_stay_unpaginated(member_client):
    res = member_client.get(reverse("notification-list"))

    assert res.status_code == 200
    assert isinstance(res.data, list)
