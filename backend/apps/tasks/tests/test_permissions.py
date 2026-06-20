import pytest
from rest_framework.test import APIRequestFactory

from apps.tasks.models import Task
from apps.tasks.permissions import CanEditTask, visible_tasks

pytestmark = pytest.mark.django_db


@pytest.fixture
def make_request():
    factory = APIRequestFactory()

    def _make(user):
        request = factory.get("/")
        request.user = user
        return request

    return _make


def _team_task(creator, team):
    return Task.objects.create(
        title="Team task",
        created_by=creator,
        assignee_type=Task.AssigneeType.TEAM,
        assignee_team=team,
    )


def test_admin_sees_all_tasks(admin_user, creator, team):
    _team_task(creator, team)
    assert visible_tasks(admin_user).count() == 1


def test_member_sees_their_team_task(team_member, creator, team):
    _team_task(creator, team)
    assert visible_tasks(team_member).count() == 1


def test_outsider_sees_no_task(outsider_user, creator, team):
    _team_task(creator, team)
    assert visible_tasks(outsider_user).count() == 0


def test_member_sees_department_task(team_member, creator, department):
    Task.objects.create(
        title="Dept task",
        created_by=creator,
        assignee_type=Task.AssigneeType.DEPARTMENT,
        assignee_department=department,
    )
    assert visible_tasks(team_member).count() == 1


def test_creator_can_edit(make_request, creator, team):
    task = _team_task(creator, team)
    assert CanEditTask().has_object_permission(make_request(creator), None, task) is True


def test_leader_can_edit_team_task(make_request, team_leader, creator, team):
    task = _team_task(creator, team)
    assert CanEditTask().has_object_permission(make_request(team_leader), None, task) is True


def test_member_cannot_edit_team_task(make_request, team_member, creator, team):
    task = _team_task(creator, team)
    assert CanEditTask().has_object_permission(make_request(team_member), None, task) is False


def test_admin_can_edit(make_request, admin_user, creator, team):
    task = _team_task(creator, team)
    assert CanEditTask().has_object_permission(make_request(admin_user), None, task) is True
