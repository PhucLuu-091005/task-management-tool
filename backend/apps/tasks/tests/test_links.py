import pytest
from django.urls import reverse

from apps.tasks.models import TaskLink
from apps.tasks.tests.helpers import team_task

pytestmark = pytest.mark.django_db


def _list_url(task):
    return reverse("task-link-list", args=[task.id])


def _detail_url(task, link):
    return reverse("task-link-detail", args=[task.id, link.id])


def test_add_link(member_client, team_member, team, creator):
    task = team_task(creator, team)

    res = member_client.post(
        _list_url(task), {"url": "https://docs.example.com/spec", "label": "Spec"}
    )

    assert res.status_code == 201
    link = TaskLink.objects.get(id=res.data["id"])
    assert link.task_id == task.id
    assert link.added_by_id == team_member.id
    assert link.url == "https://docs.example.com/spec"
    assert link.label == "Spec"


def test_label_is_optional(member_client, team, creator):
    task = team_task(creator, team)

    res = member_client.post(_list_url(task), {"url": "https://example.com"})

    assert res.status_code == 201
    assert TaskLink.objects.get(id=res.data["id"]).label == ""


def test_add_link_rejects_invalid_url(member_client, team, creator):
    task = team_task(creator, team)

    res = member_client.post(_list_url(task), {"url": "not a url"})

    assert res.status_code == 400
    assert "url" in res.data


def test_add_link_rejects_non_http_scheme(member_client, team, creator):
    task = team_task(creator, team)

    res = member_client.post(_list_url(task), {"url": "ftp://files.example.com/spec.pdf"})

    assert res.status_code == 400
    assert "url" in res.data


def test_add_link_requires_url(member_client, team, creator):
    task = team_task(creator, team)

    res = member_client.post(_list_url(task), {"label": "no url"})

    assert res.status_code == 400
    assert "url" in res.data


def test_accepts_long_urls(member_client, team, creator):
    task = team_task(creator, team)
    url = "https://example.com/" + "a" * 300

    res = member_client.post(_list_url(task), {"url": url})

    assert res.status_code == 201


def test_list_links_newest_first(member_client, team, creator):
    task = team_task(creator, team)
    TaskLink.objects.create(task=task, added_by=creator, url="https://a.example.com")
    TaskLink.objects.create(task=task, added_by=creator, url="https://b.example.com")

    res = member_client.get(_list_url(task))

    assert res.status_code == 200
    assert [row["url"] for row in res.data] == [
        "https://b.example.com",
        "https://a.example.com",
    ]


def test_links_scoped_to_visible_task(member_client, other_team, creator):
    hidden = team_task(creator, other_team)

    res = member_client.get(_list_url(hidden))

    assert res.status_code == 404


def test_add_link_on_hidden_task_is_404(member_client, other_team, creator):
    hidden = team_task(creator, other_team)

    res = member_client.post(_list_url(hidden), {"url": "https://example.com"})

    assert res.status_code == 404


def test_adder_can_delete_own_link(member_client, team_member, team, creator):
    task = team_task(creator, team)
    link = TaskLink.objects.create(task=task, added_by=team_member, url="https://example.com")

    res = member_client.delete(_detail_url(task, link))

    assert res.status_code == 204
    assert not TaskLink.objects.filter(id=link.id).exists()


def test_member_cannot_delete_others_link(member_client, team, creator, admin_user):
    task = team_task(creator, team)
    link = TaskLink.objects.create(task=task, added_by=admin_user, url="https://example.com")

    res = member_client.delete(_detail_url(task, link))

    assert res.status_code == 403


def test_leader_can_delete_any_link(leader_client, team, creator, admin_user):
    task = team_task(creator, team)
    link = TaskLink.objects.create(task=task, added_by=admin_user, url="https://example.com")

    res = leader_client.delete(_detail_url(task, link))

    assert res.status_code == 204


def test_dept_lead_can_delete_any_link(dept_lead_client, team, creator, admin_user):
    task = team_task(creator, team)
    link = TaskLink.objects.create(task=task, added_by=admin_user, url="https://example.com")

    res = dept_lead_client.delete(_detail_url(task, link))

    assert res.status_code == 204


def test_admin_can_delete_any_link(admin_client, team, creator, member_user):
    task = team_task(creator, team)
    link = TaskLink.objects.create(task=task, added_by=member_user, url="https://example.com")

    res = admin_client.delete(_detail_url(task, link))

    assert res.status_code == 204


def test_unauthenticated_cannot_list_links(api_client, team, creator):
    task = team_task(creator, team)

    res = api_client.get(_list_url(task))

    assert res.status_code in (401, 403)


def test_unauthenticated_cannot_delete_link(api_client, team, creator):
    task = team_task(creator, team)
    link = TaskLink.objects.create(task=task, added_by=creator, url="https://example.com")

    res = api_client.delete(_detail_url(task, link))

    assert res.status_code in (401, 403)


def test_delete_via_wrong_task_url_is_404(member_client, team_member, team, creator):
    task_a = team_task(creator, team)
    task_b = team_task(creator, team)
    link = TaskLink.objects.create(task=task_b, added_by=team_member, url="https://example.com")

    res = member_client.delete(_detail_url(task_a, link))

    assert res.status_code == 404


def test_links_deleted_with_task(team, creator):
    task = team_task(creator, team)
    TaskLink.objects.create(task=task, added_by=creator, url="https://example.com")

    task.delete()

    assert TaskLink.objects.count() == 0
