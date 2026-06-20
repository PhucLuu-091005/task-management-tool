import pytest

from apps.tasks.serializers import TaskSerializer

pytestmark = pytest.mark.django_db


def test_valid_user_assignment(member_user):
    s = TaskSerializer(data={"title": "T", "assignee_type": "user", "assignee_user": member_user.id})
    assert s.is_valid(), s.errors


def test_valid_team_assignment(team):
    s = TaskSerializer(data={"title": "T", "assignee_type": "team", "assignee_team": team.id})
    assert s.is_valid(), s.errors


def test_valid_department_assignment(department):
    s = TaskSerializer(
        data={"title": "T", "assignee_type": "department", "assignee_department": department.id}
    )
    assert s.is_valid(), s.errors


def test_missing_matching_assignee_is_invalid(team):
    s = TaskSerializer(data={"title": "T", "assignee_type": "user", "assignee_team": team.id})
    assert not s.is_valid()
    assert "assignee_user" in str(s.errors)


def test_extra_assignee_is_invalid(member_user, team):
    s = TaskSerializer(
        data={
            "title": "T",
            "assignee_type": "user",
            "assignee_user": member_user.id,
            "assignee_team": team.id,
        }
    )
    assert not s.is_valid()


def test_status_and_created_by_are_read_only():
    s = TaskSerializer()
    assert s.fields["status"].read_only
    assert s.fields["created_by"].read_only
    assert s.fields["is_overdue"].read_only
