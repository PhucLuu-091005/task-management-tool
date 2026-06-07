from django.urls import path

from apps.teams.views import (
    TeamDetailView,
    TeamListCreateView,
    TeamMemberCreateView,
    TeamMemberDetailView,
)

urlpatterns = [
    path("", TeamListCreateView.as_view(), name="team-list"),
    path("<int:pk>/", TeamDetailView.as_view(), name="team-detail"),
    path("<int:team_id>/members/", TeamMemberCreateView.as_view(), name="team-member-add"),
    path(
        "<int:team_id>/members/<int:user_id>/",
        TeamMemberDetailView.as_view(),
        name="team-member-detail",
    ),
]
