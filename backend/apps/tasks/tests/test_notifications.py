import pytest
from django.urls import reverse

from apps.tasks.models import Task

pytestmark = pytest.mark.django_db


def test_create_team_task_emails_leader(admin_client, team, team_leader, mailoutbox):
    # team_leader fixture adds a LEADER membership on `team`; admin creates so the
    # leader is a pure recipient, not the acting user (who is skipped).
    res = admin_client.post(
        reverse("task-list"),
        {"title": "New", "assignee_type": "team", "assignee_team": team.id},
        format="json",
    )
    assert res.status_code == 201
    assert [m.to for m in mailoutbox] == [[team_leader.email]]


def test_create_user_task_emails_assignee(admin_client, admin_user, member_user, mailoutbox):
    res = admin_client.post(
        reverse("task-list"),
        {"title": "For you", "assignee_type": "user", "assignee_user": member_user.id},
        format="json",
    )
    assert res.status_code == 201
    assert [m.to for m in mailoutbox] == [[member_user.email]]


def test_creator_self_assignment_no_email(leader_client, team_leader, mailoutbox):
    res = leader_client.post(
        reverse("task-list"),
        {"title": "Mine", "assignee_type": "user", "assignee_user": team_leader.id},
        format="json",
    )
    assert res.status_code == 201
    assert mailoutbox == []


def test_descriptive_patch_does_not_email(admin_client, creator, team, team_leader, mailoutbox):
    task = Task.objects.create(
        title="T",
        created_by=creator,
        assignee_type=Task.AssigneeType.TEAM,
        assignee_team=team,
    )
    res = admin_client.patch(
        reverse("task-detail", args=[task.id]), {"title": "Renamed"}, format="json"
    )
    assert res.status_code == 200
    assert mailoutbox == []


def test_reassignment_emails_new_target(
    admin_client, creator, team, team_leader, member_user, mailoutbox
):
    task = Task.objects.create(
        title="T",
        created_by=creator,
        assignee_type=Task.AssigneeType.TEAM,
        assignee_team=team,
    )
    res = admin_client.patch(
        reverse("task-detail", args=[task.id]),
        {"assignee_type": "user", "assignee_user": member_user.id},
        format="json",
    )
    assert res.status_code == 200
    assert [m.to for m in mailoutbox] == [[member_user.email]]
