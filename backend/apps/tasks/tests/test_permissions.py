import pytest
from django.contrib.auth.models import AnonymousUser
from rest_framework.test import APIRequestFactory

from apps.tasks.models import Task
from apps.tasks.permissions import CanEditTask, IsTaskTeamMember, visible_tasks
from apps.teams.models import TeamMembership

pytestmark = pytest.mark.django_db


@pytest.fixture
def make_request():
    factory = APIRequestFactory()

    def _make(user):
        request = factory.get("/")
        request.user = user
        return request

    return _make


# --- IsTaskTeamMember (view-level create guard) ---


def test_create_guard_allows_authenticated(make_request, member_user):
    assert IsTaskTeamMember().has_permission(make_request(member_user), None) is True


def test_create_guard_denies_anonymous(make_request):
    assert IsTaskTeamMember().has_permission(make_request(AnonymousUser()), None) is False


# --- CanEditTask (object-level edit/delete) ---


def test_creator_can_edit_own_task(make_request, team, creator):
    task = Task.objects.create(title="Mine", team=team, created_by=creator)
    assert CanEditTask().has_object_permission(make_request(creator), None, task) is True


def test_leader_of_team_can_edit_task(make_request, team, creator, leader_user):
    TeamMembership.objects.create(
        user=leader_user, team=team, role=TeamMembership.Role.LEADER
    )
    task = Task.objects.create(title="Lead", team=team, created_by=creator)
    assert CanEditTask().has_object_permission(make_request(leader_user), None, task) is True


def test_admin_can_edit_any_task(make_request, team, creator, admin_user):
    task = Task.objects.create(title="Any", team=team, created_by=creator)
    assert CanEditTask().has_object_permission(make_request(admin_user), None, task) is True


def test_plain_member_cannot_edit_others_task(make_request, team, creator, member_user):
    TeamMembership.objects.create(
        user=member_user, team=team, role=TeamMembership.Role.MEMBER
    )
    task = Task.objects.create(title="Theirs", team=team, created_by=creator)
    assert CanEditTask().has_object_permission(make_request(member_user), None, task) is False


def test_outsider_cannot_edit_task(make_request, team, creator, outsider_user):
    task = Task.objects.create(title="Out", team=team, created_by=creator)
    assert CanEditTask().has_object_permission(make_request(outsider_user), None, task) is False


def test_anonymous_cannot_edit_task(make_request, team, creator):
    task = Task.objects.create(title="Anon", team=team, created_by=creator)
    assert (
        CanEditTask().has_object_permission(make_request(AnonymousUser()), None, task)
        is False
    )


# --- visible_tasks (shared team board scoping) ---


def test_admin_sees_all_tasks(team, other_team, creator, admin_user):
    a = Task.objects.create(title="A", team=team, created_by=creator)
    b = Task.objects.create(title="B", team=other_team, created_by=creator)
    visible = visible_tasks(admin_user)
    assert a in visible
    assert b in visible


def test_member_sees_only_own_team_tasks(team, other_team, creator, member_user):
    TeamMembership.objects.create(
        user=member_user, team=team, role=TeamMembership.Role.MEMBER
    )
    mine = Task.objects.create(title="Mine", team=team, created_by=creator)
    hidden = Task.objects.create(title="Hidden", team=other_team, created_by=creator)
    visible = visible_tasks(member_user)
    assert mine in visible
    assert hidden not in visible


def test_outsider_sees_no_tasks(team, creator, outsider_user):
    Task.objects.create(title="Nope", team=team, created_by=creator)
    assert visible_tasks(outsider_user).count() == 0


def test_anonymous_sees_no_tasks(team, creator):
    Task.objects.create(title="Nope", team=team, created_by=creator)
    assert visible_tasks(AnonymousUser()).count() == 0
