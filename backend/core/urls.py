from django.contrib import admin
from django.urls import include, path
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@extend_schema(responses=OpenApiTypes.OBJECT)
@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    return Response({"status": "ok"}, status=status.HTTP_200_OK)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health_check),
    path("api/users/", include("apps.users.urls")),
    path("api/teams/", include("apps.teams.urls")),
    path("api/departments/", include("apps.teams.department_urls")),
    path("api/tasks/", include("apps.tasks.urls")),
    path("api/notifications/", include("apps.notifications.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]
