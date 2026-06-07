import pytest
from rest_framework.exceptions import ValidationError

from apps.teams.models import TeamMembership
from apps.teams.serializers import TeamMemberSerializer

pytestmark = pytest.mark.django_db


def test_add_member_handles_concurrent_duplicate(team, member_user):
    # TOCTOU: validate() already passed for a request, but a concurrent one
    # committed the membership before this one reached the INSERT. The unique
    # (user, team) constraint must surface as a 400, not an unhandled 500.
    TeamMembership.objects.create(user=member_user, team=team, role=TeamMembership.Role.MEMBER)
    serializer = TeamMemberSerializer(context={"team": team})
    with pytest.raises(ValidationError):
        serializer.create({"user": member_user, "team": team, "role": TeamMembership.Role.LEADER})
