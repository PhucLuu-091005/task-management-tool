from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from apps.tasks.models import Task

pytestmark = pytest.mark.django_db


# --- Create ---


def test_member_creates_task_in_own_team(member_client, team, team_member):
    res = member_client.post(
        reverse("task-list"), {"title": "New work", "team": team.id}, format="json"
    )
    assert res.status_code == 201
    task = Task.objects.get(title="New work")
    assert task.team == team
    assert task.created_by == team_member
    assert task.status == Task.Status.NEW


def test_create_sets_created_by_to_request_user(leader_client, team, team_leader):
    res = leader_client.post(
        reverse("task-list"), {"title": "Lead work", "team": team.id}, format="json"
    )
    assert res.status_code == 201
    assert Task.objects.get(title="Lead work").created_by == team_leader


def test_admin_creates_task_in_any_team(admin_client, team):
    res = admin_client.post(
        reverse("task-list"), {"title": "Admin work", "team": team.id}, format="json"
    )
    assert res.status_code == 201


def test_outsider_cannot_create_task_in_team(outsider_client, team):
    res = outsider_client.post(
        reverse("task-list"), {"title": "Sneaky", "team": team.id}, format="json"
    )
    assert res.status_code == 400
    assert "team" in res.data


def test_create_task_requires_auth(api_client, team):
    res = api_client.post(reverse("task-list"), {"title": "X", "team": team.id}, format="json")
    assert res.status_code == 401


def test_create_ignores_client_supplied_status_and_assignee(
    member_client, team, team_member, assignee
):
    res = member_client.post(
        reverse("task-list"),
        {
            "title": "Locked",
            "team": team.id,
            "status": Task.Status.DONE,
            "assignee": assignee.id,
        },
        format="json",
    )
    assert res.status_code == 201
    task = Task.objects.get(title="Locked")
    assert task.status == Task.Status.NEW
    assert task.assignee is None


# --- List visibility ---


def test_member_lists_only_own_team_tasks(member_client, team, other_team, team_member):
    Task.objects.create(title="Mine", team=team, created_by=team_member)
    Task.objects.create(title="Hidden", team=other_team, created_by=team_member)
    res = member_client.get(reverse("task-list"))
    assert res.status_code == 200
    titles = [t["title"] for t in res.data]
    assert "Mine" in titles
    assert "Hidden" not in titles


def test_admin_lists_all_tasks(admin_client, team, other_team, admin_user):
    Task.objects.create(title="One", team=team, created_by=admin_user)
    Task.objects.create(title="Two", team=other_team, created_by=admin_user)
    res = admin_client.get(reverse("task-list"))
    assert res.status_code == 200
    titles = [t["title"] for t in res.data]
    assert "One" in titles
    assert "Two" in titles


def test_outsider_lists_no_tasks(outsider_client, team, admin_user):
    Task.objects.create(title="Nope", team=team, created_by=admin_user)
    res = outsider_client.get(reverse("task-list"))
    assert res.status_code == 200
    assert res.data == []


def test_list_requires_auth(api_client):
    res = api_client.get(reverse("task-list"))
    assert res.status_code == 401


# --- Retrieve ---


def test_member_retrieves_own_team_task(member_client, team, team_member):
    task = Task.objects.create(title="Visible", team=team, created_by=team_member)
    res = member_client.get(reverse("task-detail", args=[task.id]))
    assert res.status_code == 200
    assert res.data["title"] == "Visible"


def test_outsider_cannot_retrieve_task_returns_404(outsider_client, team, admin_user):
    task = Task.objects.create(title="Hidden", team=team, created_by=admin_user)
    res = outsider_client.get(reverse("task-detail", args=[task.id]))
    assert res.status_code == 404


# --- Update ---


def test_creator_updates_own_task(member_client, team, team_member):
    task = Task.objects.create(title="Editable", team=team, created_by=team_member)
    res = member_client.patch(
        reverse("task-detail", args=[task.id]), {"description": "Updated"}, format="json"
    )
    assert res.status_code == 200
    task.refresh_from_db()
    assert task.description == "Updated"


def test_leader_updates_any_task_in_team(leader_client, team, team_leader, admin_user):
    task = Task.objects.create(title="Lead edits", team=team, created_by=admin_user)
    res = leader_client.patch(
        reverse("task-detail", args=[task.id]), {"description": "By leader"}, format="json"
    )
    assert res.status_code == 200
    task.refresh_from_db()
    assert task.description == "By leader"


def test_admin_updates_any_task(admin_client, team, member_user):
    task = Task.objects.create(title="Admin edits", team=team, created_by=member_user)
    res = admin_client.patch(
        reverse("task-detail", args=[task.id]), {"priority": Task.Priority.URGENT}, format="json"
    )
    assert res.status_code == 200
    task.refresh_from_db()
    assert task.priority == Task.Priority.URGENT


def test_plain_member_cannot_update_others_task(member_client, team, team_member, admin_user):
    task = Task.objects.create(title="Not yours", team=team, created_by=admin_user)
    res = member_client.patch(
        reverse("task-detail", args=[task.id]), {"description": "nope"}, format="json"
    )
    assert res.status_code == 403


def test_update_cannot_change_status_field(member_client, team, team_member):
    task = Task.objects.create(title="Locked status", team=team, created_by=team_member)
    res = member_client.patch(
        reverse("task-detail", args=[task.id]), {"status": Task.Status.DONE}, format="json"
    )
    assert res.status_code == 200
    task.refresh_from_db()
    assert task.status == Task.Status.NEW


# --- Delete ---


def test_creator_deletes_own_task(member_client, team, team_member):
    task = Task.objects.create(title="Deletable", team=team, created_by=team_member)
    res = member_client.delete(reverse("task-detail", args=[task.id]))
    assert res.status_code == 204
    assert not Task.objects.filter(id=task.id).exists()


def test_plain_member_cannot_delete_others_task(member_client, team, team_member, admin_user):
    task = Task.objects.create(title="Keep", team=team, created_by=admin_user)
    res = member_client.delete(reverse("task-detail", args=[task.id]))
    assert res.status_code == 403
    assert Task.objects.filter(id=task.id).exists()


def test_detail_requires_auth(api_client, team, admin_user):
    task = Task.objects.create(title="Auth", team=team, created_by=admin_user)
    res = api_client.get(reverse("task-detail", args=[task.id]))
    assert res.status_code == 401


# --- Filters & search ---


def test_filter_by_status(member_client, team, team_member):
    new_task = Task.objects.create(title="Fresh", team=team, created_by=team_member)
    Task.objects.create(
        title="Working",
        team=team,
        created_by=team_member,
        status=Task.Status.IN_PROGRESS,
    )
    res = member_client.get(reverse("task-list"), {"status": Task.Status.NEW})
    assert res.status_code == 200
    titles = [t["title"] for t in res.data]
    assert titles == ["Fresh"]
    assert new_task.title in titles


def test_filter_by_priority(member_client, team, team_member):
    Task.objects.create(
        title="Low one", team=team, created_by=team_member, priority=Task.Priority.LOW
    )
    Task.objects.create(
        title="Urgent one",
        team=team,
        created_by=team_member,
        priority=Task.Priority.URGENT,
    )
    res = member_client.get(reverse("task-list"), {"priority": Task.Priority.URGENT})
    assert res.status_code == 200
    assert [t["title"] for t in res.data] == ["Urgent one"]


def test_filter_by_assignee(member_client, team, team_member, assignee):
    Task.objects.create(title="Assigned", team=team, created_by=team_member, assignee=assignee)
    Task.objects.create(title="Unassigned", team=team, created_by=team_member)
    res = member_client.get(reverse("task-list"), {"assignee": assignee.id})
    assert res.status_code == 200
    assert [t["title"] for t in res.data] == ["Assigned"]


def test_filter_is_overdue_true(member_client, team, team_member):
    Task.objects.create(
        title="Late",
        team=team,
        created_by=team_member,
        due_date=timezone.now() - timedelta(hours=1),
    )
    Task.objects.create(
        title="On time",
        team=team,
        created_by=team_member,
        due_date=timezone.now() + timedelta(days=1),
    )
    res = member_client.get(reverse("task-list"), {"is_overdue": "true"})
    assert res.status_code == 200
    assert [t["title"] for t in res.data] == ["Late"]


def test_filter_is_overdue_false(member_client, team, team_member):
    Task.objects.create(
        title="Late",
        team=team,
        created_by=team_member,
        due_date=timezone.now() - timedelta(hours=1),
    )
    Task.objects.create(
        title="On time",
        team=team,
        created_by=team_member,
        due_date=timezone.now() + timedelta(days=1),
    )
    res = member_client.get(reverse("task-list"), {"is_overdue": "false"})
    assert res.status_code == 200
    titles = [t["title"] for t in res.data]
    assert "On time" in titles
    assert "Late" not in titles


def test_search_by_title(member_client, team, team_member):
    Task.objects.create(title="Refactor auth", team=team, created_by=team_member)
    Task.objects.create(title="Write docs", team=team, created_by=team_member)
    res = member_client.get(reverse("task-list"), {"search": "auth"})
    assert res.status_code == 200
    assert [t["title"] for t in res.data] == ["Refactor auth"]


def test_invalid_priority_param_returns_400(member_client, team, team_member):
    res = member_client.get(reverse("task-list"), {"priority": "abc"})
    assert res.status_code == 400


def test_invalid_assignee_param_returns_400(member_client, team, team_member):
    res = member_client.get(reverse("task-list"), {"assignee": "notanint"})
    assert res.status_code == 400
