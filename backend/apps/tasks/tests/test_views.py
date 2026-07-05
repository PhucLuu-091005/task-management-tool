from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from apps.tasks.models import Task
from apps.tasks.tests.helpers import team_task
from apps.teams.models import Department, Team

pytestmark = pytest.mark.django_db


def test_leader_creates_task_in_own_team_sets_created_by(leader_client, team_leader, team):
    res = leader_client.post(
        reverse("task-list"),
        {"title": "New", "assignee_type": "team", "assignee_team": team.id},
        format="json",
    )
    assert res.status_code == 201
    task = Task.objects.get(id=res.data["id"])
    assert task.created_by == team_leader
    assert task.status == Task.Status.NEW


def test_member_cannot_create_task(member_client, team):
    res = member_client.post(
        reverse("task-list"),
        {"title": "New", "assignee_type": "team", "assignee_team": team.id},
        format="json",
    )
    assert res.status_code == 403


def test_leader_cannot_create_task_for_other_team(leader_client, team_leader, other_team):
    res = leader_client.post(
        reverse("task-list"),
        {"title": "New", "assignee_type": "team", "assignee_team": other_team.id},
        format="json",
    )
    assert res.status_code == 403


def test_admin_can_create_task_for_any_team(admin_client, other_team):
    res = admin_client.post(
        reverse("task-list"),
        {"title": "New", "assignee_type": "team", "assignee_team": other_team.id},
        format="json",
    )
    assert res.status_code == 201


def test_leader_can_create_user_task_for_team_member(leader_client, team_leader, team_member):
    res = leader_client.post(
        reverse("task-list"),
        {"title": "New", "assignee_type": "user", "assignee_user": team_member.id},
        format="json",
    )
    assert res.status_code == 201


def test_leader_cannot_create_user_task_for_non_member(leader_client, team_leader, outsider_user):
    res = leader_client.post(
        reverse("task-list"),
        {"title": "New", "assignee_type": "user", "assignee_user": outsider_user.id},
        format="json",
    )
    assert res.status_code == 403


def test_leader_cannot_create_department_task(leader_client, team_leader, department):
    # A team leader has no authority over department-scoped tasks, even in their own department.
    res = leader_client.post(
        reverse("task-list"),
        {"title": "New", "assignee_type": "department", "assignee_department": department.id},
        format="json",
    )
    assert res.status_code == 403


def test_department_lead_can_create_department_task(dept_lead_client, department):
    res = dept_lead_client.post(
        reverse("task-list"),
        {"title": "New", "assignee_type": "department", "assignee_department": department.id},
        format="json",
    )
    assert res.status_code == 201


def test_department_lead_can_edit_others_department_task(dept_lead_client, creator, department):
    # A dept task created by someone else must be visible to the lead so they can edit it.
    task = Task.objects.create(
        title="Dept",
        created_by=creator,
        assignee_type=Task.AssigneeType.DEPARTMENT,
        assignee_department=department,
    )
    res = dept_lead_client.patch(
        reverse("task-detail", args=[task.id]), {"title": "Renamed"}, format="json"
    )
    assert res.status_code == 200
    task.refresh_from_db()
    assert task.title == "Renamed"


def test_department_lead_can_create_team_task_in_their_department(dept_lead_client, team):
    res = dept_lead_client.post(
        reverse("task-list"),
        {"title": "New", "assignee_type": "team", "assignee_team": team.id},
        format="json",
    )
    assert res.status_code == 201


def test_department_lead_can_create_user_task_for_department_member(dept_lead_client, team_member):
    res = dept_lead_client.post(
        reverse("task-list"),
        {"title": "New", "assignee_type": "user", "assignee_user": team_member.id},
        format="json",
    )
    assert res.status_code == 201


def test_department_lead_can_edit_team_task_in_their_department(dept_lead_client, creator, team):
    task = team_task(creator, team)
    res = dept_lead_client.patch(
        reverse("task-detail", args=[task.id]), {"title": "Renamed"}, format="json"
    )
    assert res.status_code == 200
    task.refresh_from_db()
    assert task.title == "Renamed"


def test_department_lead_cannot_manage_team_in_other_department(dept_lead_client):
    other_dept = Department.objects.create(name="Sales")
    foreign_team = Team.objects.create(name="Outside", department=other_dept)
    res = dept_lead_client.post(
        reverse("task-list"),
        {"title": "New", "assignee_type": "team", "assignee_team": foreign_team.id},
        format="json",
    )
    assert res.status_code == 403


def test_member_can_retrieve_visible_team_task(member_client, creator, team):
    task = team_task(creator, team)
    res = member_client.get(reverse("task-detail", args=[task.id]))
    assert res.status_code == 200
    assert res.data["id"] == task.id


def test_member_can_retrieve_visible_department_task(member_client, creator, department):
    task = Task.objects.create(
        title="Dept task",
        created_by=creator,
        assignee_type=Task.AssigneeType.DEPARTMENT,
        assignee_department=department,
    )
    res = member_client.get(reverse("task-detail", args=[task.id]))
    assert res.status_code == 200
    assert res.data["id"] == task.id


def test_title_over_max_length_returns_400(admin_client, team):
    res = admin_client.post(
        reverse("task-list"),
        {"title": "x" * 201, "assignee_type": "team", "assignee_team": team.id},
        format="json",
    )
    assert res.status_code == 400


def test_list_scoped_to_visible(member_client, creator, team, other_team):
    team_task(creator, team, title="Visible")
    team_task(creator, other_team, title="Hidden")
    res = member_client.get(reverse("task-list"))
    assert res.status_code == 200
    titles = {t["title"] for t in res.data["results"]}
    assert "Visible" in titles and "Hidden" not in titles


def test_outsider_gets_404_on_detail(outsider_client, creator, team):
    task = team_task(creator, team)
    res = outsider_client.get(reverse("task-detail", args=[task.id]))
    assert res.status_code == 404


def test_member_cannot_update_team_task(member_client, creator, team):
    task = team_task(creator, team)
    res = member_client.patch(reverse("task-detail", args=[task.id]), {"title": "changed"})
    assert res.status_code == 403


def test_member_cannot_delete_team_task(member_client, creator, team):
    task = team_task(creator, team)
    res = member_client.delete(reverse("task-detail", args=[task.id]))
    assert res.status_code == 403


def test_leader_can_delete_team_task(leader_client, creator, team):
    task = team_task(creator, team)
    res = leader_client.delete(reverse("task-detail", args=[task.id]))
    assert res.status_code == 204


def test_filter_by_status(admin_client, creator, team):
    team_task(creator, team, title="New one")
    team_task(creator, team, title="Done one", status=Task.Status.DONE)
    res = admin_client.get(reverse("task-list"), {"status": "done"})
    assert [t["title"] for t in res.data["results"]] == ["Done one"]


def test_search_by_title(admin_client, creator, team):
    team_task(creator, team, title="Deploy pipeline")
    team_task(creator, team, title="Write docs")
    res = admin_client.get(reverse("task-list"), {"search": "deploy"})
    assert [t["title"] for t in res.data["results"]] == ["Deploy pipeline"]


def test_invalid_assignee_user_filter_returns_400(admin_client):
    res = admin_client.get(reverse("task-list"), {"assignee_user": "abc"})
    assert res.status_code == 400


def test_patch_change_type_nulls_stale_assignee(admin_client, creator, team, member_user):
    task = team_task(creator, team)
    url = reverse("task-detail", args=[task.id])
    res = admin_client.patch(
        url,
        {"assignee_type": "user", "assignee_user": member_user.id},
        format="json",
    )
    assert res.status_code == 200
    task.refresh_from_db()
    assert task.assignee_type == Task.AssigneeType.USER
    assert task.assignee_user_id == member_user.id
    assert task.assignee_team_id is None


def test_is_overdue_true_filters_by_stored_status(admin_client, creator, team):
    past = timezone.now() - timedelta(days=1)
    team_task(creator, team, title="Flipped", status=Task.Status.OVERDUE, due_date=past)
    # Past-due but not yet flipped: stored status is the source of truth, so not overdue.
    team_task(creator, team, title="Not flipped", status=Task.Status.NEW, due_date=past)
    res = admin_client.get(reverse("task-list"), {"is_overdue": "true"})
    assert [t["title"] for t in res.data["results"]] == ["Flipped"]


def test_is_overdue_false_excludes_stored_overdue(admin_client, creator, team):
    past = timezone.now() - timedelta(days=1)
    team_task(creator, team, title="Flipped", status=Task.Status.OVERDUE, due_date=past)
    team_task(creator, team, title="Not flipped", status=Task.Status.NEW, due_date=past)
    res = admin_client.get(reverse("task-list"), {"is_overdue": "false"})
    assert [t["title"] for t in res.data["results"]] == ["Not flipped"]


def test_patch_add_mismatched_assignee_rejected(admin_client, creator, team, member_user):
    task = team_task(creator, team)
    url = reverse("task-detail", args=[task.id])
    res = admin_client.patch(
        url,
        {"assignee_user": member_user.id},
        format="json",
    )
    assert res.status_code == 400


def test_patch_change_type_without_new_assignee_rejected(admin_client, creator, team):
    task = team_task(creator, team)
    url = reverse("task-detail", args=[task.id])
    res = admin_client.patch(
        url,
        {"assignee_type": "user"},
        format="json",
    )
    assert res.status_code == 400


def test_patch_descriptive_only_keeps_assignee(admin_client, creator, team):
    task = team_task(creator, team)
    url = reverse("task-detail", args=[task.id])
    res = admin_client.patch(url, {"title": "Renamed"}, format="json")
    assert res.status_code == 200
    task.refresh_from_db()
    assert task.title == "Renamed"
    assert task.assignee_team_id == team.id


def test_create_sets_assigned_at(admin_client, team):
    res = admin_client.post(
        reverse("task-list"),
        {"title": "New", "assignee_type": "team", "assignee_team": team.id},
        format="json",
    )
    assert res.status_code == 201
    task = Task.objects.get(id=res.data["id"])
    assert task.assigned_at is not None


def test_reassign_sets_assigned_at(admin_client, creator, member_user):
    # Created directly so assigned_at starts empty, isolating the reassign write path.
    task = Task.objects.create(
        title="T",
        created_by=creator,
        assignee_type=Task.AssigneeType.USER,
        assignee_user=member_user,
    )
    assert task.assigned_at is None
    res = admin_client.patch(
        reverse("task-detail", args=[task.id]),
        {"assignee_user": creator.id},
        format="json",
    )
    assert res.status_code == 200
    task.refresh_from_db()
    assert task.assigned_at is not None


def test_descriptive_update_leaves_assigned_at_untouched(admin_client, creator, member_user):
    task = Task.objects.create(
        title="T",
        created_by=creator,
        assignee_type=Task.AssigneeType.USER,
        assignee_user=member_user,
    )
    res = admin_client.patch(
        reverse("task-detail", args=[task.id]), {"title": "Renamed"}, format="json"
    )
    assert res.status_code == 200
    task.refresh_from_db()
    assert task.assigned_at is None
