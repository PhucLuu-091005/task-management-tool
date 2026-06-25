import pytest
from django.urls import reverse

from apps.notifications.models import Notification
from apps.tasks.models import Task

pytestmark = pytest.mark.django_db


def test_create_team_task_notifies_leader(member_client, team_member, team, team_leader):
    # team_leader fixture adds a LEADER membership on `team`
    res = member_client.post(
        reverse("task-list"),
        {"title": "New", "assignee_type": "team", "assignee_team": team.id},
        format="json",
    )
    assert res.status_code == 201
    assert list(Notification.objects.values_list("recipient_id", flat=True)) == [team_leader.id]


def test_create_user_task_notifies_assignee(admin_client, admin_user, member_user):
    res = admin_client.post(
        reverse("task-list"),
        {"title": "For you", "assignee_type": "user", "assignee_user": member_user.id},
        format="json",
    )
    assert res.status_code == 201
    assert list(Notification.objects.values_list("recipient_id", flat=True)) == [member_user.id]


def test_creator_self_assignment_no_notification(member_client, team_member):
    res = member_client.post(
        reverse("task-list"),
        {"title": "Mine", "assignee_type": "user", "assignee_user": team_member.id},
        format="json",
    )
    assert res.status_code == 201
    assert Notification.objects.count() == 0


def test_descriptive_patch_does_not_notify(admin_client, creator, team, team_leader):
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
    assert Notification.objects.count() == 0


def test_reassignment_notifies_new_target(admin_client, creator, team, team_leader, member_user):
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
    assert list(Notification.objects.values_list("recipient_id", flat=True)) == [member_user.id]
