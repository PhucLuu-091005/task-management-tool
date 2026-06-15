from decimal import Decimal

import pytest
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory

from apps.tasks.models import Task
from apps.tasks.serializers import TaskSerializer
from apps.teams.models import TeamMembership

pytestmark = pytest.mark.django_db


@pytest.fixture
def make_context():
    factory = APIRequestFactory()

    def _make(user):
        request = factory.post("/")
        request.user = user
        return {"request": request}

    return _make


def test_member_can_create_task_in_own_team(make_context, team, member_user):
    TeamMembership.objects.create(user=member_user, team=team, role=TeamMembership.Role.MEMBER)
    serializer = TaskSerializer(
        data={"title": "Do it", "team": team.id}, context=make_context(member_user)
    )
    assert serializer.is_valid(), serializer.errors


def test_leader_can_create_task_in_own_team(make_context, team, leader_user):
    TeamMembership.objects.create(user=leader_user, team=team, role=TeamMembership.Role.LEADER)
    serializer = TaskSerializer(
        data={"title": "Lead it", "team": team.id}, context=make_context(leader_user)
    )
    assert serializer.is_valid(), serializer.errors


def test_admin_can_create_task_in_any_team(make_context, team, admin_user):
    serializer = TaskSerializer(
        data={"title": "Admin task", "team": team.id},
        context=make_context(admin_user),
    )
    assert serializer.is_valid(), serializer.errors


def test_non_member_cannot_create_task_in_team(make_context, team, outsider_user):
    serializer = TaskSerializer(
        data={"title": "Sneaky", "team": team.id},
        context=make_context(outsider_user),
    )
    with pytest.raises(ValidationError) as exc:
        serializer.is_valid(raise_exception=True)
    assert "team" in exc.value.detail


def test_writable_descriptive_fields_round_trip(make_context, team, member_user):
    TeamMembership.objects.create(user=member_user, team=team, role=TeamMembership.Role.MEMBER)
    serializer = TaskSerializer(
        data={
            "title": "Full",
            "description": "Details",
            "priority": Task.Priority.HIGH,
            "estimate_hours": "3.25",
            "team": team.id,
        },
        context=make_context(member_user),
    )
    assert serializer.is_valid(), serializer.errors
    task = serializer.save(created_by=member_user)
    assert task.description == "Details"
    assert task.priority == Task.Priority.HIGH
    assert task.estimate_hours == Decimal("3.25")


def test_status_assignee_created_by_are_read_only(make_context, team, member_user, assignee):
    TeamMembership.objects.create(user=member_user, team=team, role=TeamMembership.Role.MEMBER)
    serializer = TaskSerializer(
        data={
            "title": "Try to cheat",
            "team": team.id,
            "status": Task.Status.DONE,
            "assignee": assignee.id,
            "created_by": assignee.id,
        },
        context=make_context(member_user),
    )
    assert serializer.is_valid(), serializer.errors
    task = serializer.save(created_by=member_user)
    assert task.status == Task.Status.NEW
    assert task.assignee is None
    assert task.created_by == member_user


def test_is_overdue_is_exposed_read_only(make_context, team, creator):
    task = Task.objects.create(title="Read", team=team, created_by=creator)
    data = TaskSerializer(task, context=make_context(creator)).data
    assert data["is_overdue"] is False
    assert "created_at" in data
