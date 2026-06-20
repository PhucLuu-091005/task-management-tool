import pytest
from django.urls import reverse

from apps.tasks.models import Task

pytestmark = pytest.mark.django_db


def _team_task(creator, team, **kwargs):
    return Task.objects.create(
        title=kwargs.pop("title", "Team task"),
        created_by=creator,
        assignee_type=Task.AssigneeType.TEAM,
        assignee_team=team,
        **kwargs,
    )


def test_create_task_sets_created_by(member_client, team_member, team):
    res = member_client.post(
        reverse("task-list"),
        {"title": "New", "assignee_type": "team", "assignee_team": team.id},
        format="json",
    )
    assert res.status_code == 201
    task = Task.objects.get(id=res.data["id"])
    assert task.created_by == team_member
    assert task.status == Task.Status.NEW


def test_list_scoped_to_visible(member_client, creator, team, other_team):
    _team_task(creator, team, title="Visible")
    Task.objects.create(
        title="Hidden",
        created_by=creator,
        assignee_type=Task.AssigneeType.TEAM,
        assignee_team=other_team,
    )
    res = member_client.get(reverse("task-list"))
    assert res.status_code == 200
    titles = {t["title"] for t in res.data}
    assert "Visible" in titles and "Hidden" not in titles


def test_outsider_gets_404_on_detail(outsider_client, creator, team):
    task = _team_task(creator, team)
    res = outsider_client.get(reverse("task-detail", args=[task.id]))
    assert res.status_code == 404


def test_member_cannot_delete_team_task(member_client, creator, team):
    task = _team_task(creator, team)
    res = member_client.delete(reverse("task-detail", args=[task.id]))
    assert res.status_code == 403


def test_leader_can_delete_team_task(leader_client, creator, team):
    task = _team_task(creator, team)
    res = leader_client.delete(reverse("task-detail", args=[task.id]))
    assert res.status_code == 204


def test_filter_by_status(admin_client, creator, team):
    _team_task(creator, team, title="New one")
    _team_task(creator, team, title="Done one", status=Task.Status.DONE)
    res = admin_client.get(reverse("task-list"), {"status": "done"})
    assert [t["title"] for t in res.data] == ["Done one"]


def test_search_by_title(admin_client, creator, team):
    _team_task(creator, team, title="Deploy pipeline")
    _team_task(creator, team, title="Write docs")
    res = admin_client.get(reverse("task-list"), {"search": "deploy"})
    assert [t["title"] for t in res.data] == ["Deploy pipeline"]


def test_invalid_assignee_user_filter_returns_400(admin_client):
    res = admin_client.get(reverse("task-list"), {"assignee_user": "abc"})
    assert res.status_code == 400


def test_patch_change_type_nulls_stale_assignee(admin_client, creator, team, member_user):
    task = _team_task(creator, team)
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


def test_patch_add_mismatched_assignee_rejected(admin_client, creator, team, member_user):
    task = _team_task(creator, team)
    url = reverse("task-detail", args=[task.id])
    res = admin_client.patch(
        url,
        {"assignee_user": member_user.id},
        format="json",
    )
    assert res.status_code == 400


def test_patch_change_type_without_new_assignee_rejected(admin_client, creator, team):
    task = _team_task(creator, team)
    url = reverse("task-detail", args=[task.id])
    res = admin_client.patch(
        url,
        {"assignee_type": "user"},
        format="json",
    )
    assert res.status_code == 400


def test_patch_descriptive_only_keeps_assignee(admin_client, creator, team):
    task = _team_task(creator, team)
    url = reverse("task-detail", args=[task.id])
    res = admin_client.patch(url, {"title": "Renamed"}, format="json")
    assert res.status_code == 200
    task.refresh_from_db()
    assert task.title == "Renamed"
    assert task.assignee_team_id == team.id
