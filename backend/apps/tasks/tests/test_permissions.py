import pytest
from rest_framework.test import APIRequestFactory

from apps.tasks.models import Task
from apps.tasks.permissions import CanEditTask, visible_tasks
from apps.tasks.tests.helpers import team_task
from apps.teams.models import TeamMembership

pytestmark = pytest.mark.django_db


@pytest.fixture
def make_request():
    factory = APIRequestFactory()

    def _make(user):
        # DELETE (a write method) so CanEditTask exercises its edit gate, not the read bypass.
        request = factory.delete("/")
        request.user = user
        return request

    return _make


def test_admin_sees_all_tasks(admin_user, team_member, creator, team, other_team):
    # Tasks a plain member cannot see must still all be visible to an admin.
    team_task(creator, team, title="My team")
    team_task(creator, other_team, title="Other team")
    assert visible_tasks(team_member).count() == 1
    assert visible_tasks(admin_user).count() == 2


def test_member_sees_their_team_task(team_member, creator, team):
    team_task(creator, team)
    assert visible_tasks(team_member).count() == 1


def test_outsider_sees_no_task(outsider_user, creator, team):
    team_task(creator, team)
    assert visible_tasks(outsider_user).count() == 0


def test_same_department_other_team_member_does_not_see_team_task(
    creator, team, other_team, member_user
):
    # Same department, but a team-scoped task stays visible to its own team only.
    TeamMembership.objects.create(
        user=member_user, team=other_team, role=TeamMembership.Role.MEMBER
    )
    team_task(creator, team)
    assert visible_tasks(member_user).count() == 0


def test_member_sees_department_task(team_member, creator, department):
    Task.objects.create(
        title="Dept task",
        created_by=creator,
        assignee_type=Task.AssigneeType.DEPARTMENT,
        assignee_department=department,
    )
    assert visible_tasks(team_member).count() == 1


def test_creator_can_edit(make_request, creator, team):
    task = team_task(creator, team)
    assert CanEditTask().has_object_permission(make_request(creator), None, task) is True


def test_leader_can_edit_team_task(make_request, team_leader, creator, team):
    task = team_task(creator, team)
    assert CanEditTask().has_object_permission(make_request(team_leader), None, task) is True


def test_member_cannot_edit_team_task(make_request, team_member, creator, team):
    task = team_task(creator, team)
    assert CanEditTask().has_object_permission(make_request(team_member), None, task) is False


def test_admin_can_edit(make_request, admin_user, creator, team):
    task = team_task(creator, team)
    assert CanEditTask().has_object_permission(make_request(admin_user), None, task) is True


def _dept_task(creator, department):
    return Task.objects.create(
        title="Dept task",
        created_by=creator,
        assignee_type=Task.AssigneeType.DEPARTMENT,
        assignee_department=department,
    )


def test_team_leader_cannot_edit_department_task(make_request, team_leader, creator, department):
    # team_leader leads a team in `department` but is not its lead → no authority over dept tasks.
    task = _dept_task(creator, department)
    assert CanEditTask().has_object_permission(make_request(team_leader), None, task) is False


def test_department_lead_can_edit_department_task(make_request, dept_lead, creator, department):
    task = _dept_task(creator, department)
    assert CanEditTask().has_object_permission(make_request(dept_lead), None, task) is True


def test_department_lead_can_edit_team_task_in_department(make_request, dept_lead, creator, team):
    # A dept lead outranks team leaders: they manage team-scoped tasks inside their department too.
    task = team_task(creator, team)
    assert CanEditTask().has_object_permission(make_request(dept_lead), None, task) is True


def test_department_lead_sees_whole_department(dept_lead, creator, team, department, member_user):
    team_task(creator, team)
    _dept_task(creator, department)
    Task.objects.create(
        title="User task",
        created_by=creator,
        assignee_type=Task.AssigneeType.USER,
        assignee_user=member_user,
    )
    TeamMembership.objects.create(user=member_user, team=team, role=TeamMembership.Role.MEMBER)
    assert visible_tasks(dept_lead).count() == 3
