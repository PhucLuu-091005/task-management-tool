from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import ProtectedError, prefetch_related_objects
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.tasks.models import Task
from apps.users.constants import (
    CANNOT_DELETE_ADMIN_ERROR_MESSAGE,
    CANNOT_DELETE_SELF_ERROR_MESSAGE,
    REFRESH_COOKIE_MISSING_ERROR_MESSAGE,
    USER_ASSIGNED_TASKS_ERROR_MESSAGE,
    USER_HAS_TASKS_ERROR_MESSAGE,
)
from apps.users.cookies import delete_refresh_cookie, set_refresh_cookie
from apps.users.managers import PROFILE_PREFETCHES
from apps.users.permissions import IsAdmin
from apps.users.serializers import (
    AvatarUpdateSerializer,
    RegisterSerializer,
    UserSerializer,
)

User = get_user_model()


class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *arg, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        prefetch_related_objects([user], *PROFILE_PREFETCHES)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class UserListView(ListAPIView):
    queryset = User.objects.with_memberships()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]


class UserDetailView(DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.id == request.user.id:
            return Response(
                {"detail": CANNOT_DELETE_SELF_ERROR_MESSAGE},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Admin accounts are undeletable through this endpoint; this also keeps at
        # least one admin around (an admin can never remove another admin or self).
        if instance.is_admin:
            return Response(
                {"detail": CANNOT_DELETE_ADMIN_ERROR_MESSAGE},
                status=status.HTTP_403_FORBIDDEN,
            )
        # assignee_user is SET_NULL, so deleting a direct assignee would leave
        # their tasks in an invalid "type=user, assignee=null" state that can't
        # be edited afterwards. Block it (like created_by) so tasks stay valid.
        if Task.objects.filter(assignee_user=instance).exists():
            return Response(
                {"detail": USER_ASSIGNED_TASKS_ERROR_MESSAGE},
                status=status.HTTP_409_CONFLICT,
            )
        try:
            instance.delete()
        except ProtectedError:
            # Task.created_by is PROTECT, so a creator can't be removed until
            # their tasks are gone; report it instead of a raw 500.
            return Response(
                {"detail": USER_HAS_TASKS_ERROR_MESSAGE},
                status=status.HTTP_409_CONFLICT,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProfileView(APIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    # Accept an avatar file (multipart) and a null clear (json) on the same route.
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request, *args, **kwargs):
        prefetch_related_objects([request.user], *PROFILE_PREFETCHES)
        return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)

    @extend_schema(request=AvatarUpdateSerializer, responses=UserSerializer)
    def patch(self, request, *args, **kwargs):
        serializer = AvatarUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        prefetch_related_objects([request.user], *PROFILE_PREFETCHES)
        return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)


class CookieTokenObtainPairView(TokenObtainPairView):
    @extend_schema(
        responses=inline_serializer(
            name="AccessTokenResponse", fields={"access": serializers.CharField()}
        ),
    )
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        refresh = response.data.pop("refresh", None)
        if refresh:
            set_refresh_cookie(response, refresh)
        return response


@method_decorator(csrf_protect, name="dispatch")
class CookieTokenRefreshView(TokenRefreshView):
    @extend_schema(
        request=None,
        responses=inline_serializer(
            name="RefreshResponse", fields={"access": serializers.CharField()}
        ),
    )
    def post(self, request, *args, **kwargs):
        token = request.COOKIES.get(settings.AUTH_REFRESH_COOKIE)
        if not token:
            return Response(
                {"detail": REFRESH_COOKIE_MISSING_ERROR_MESSAGE},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        serializer = self.get_serializer(data={"refresh": token})
        try:
            # Blacklist checks raise a raw TokenError DRF can't map to a response;
            # mirror TokenViewBase.post's conversion to InvalidToken (401).
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0]) from e
        response = Response(serializer.validated_data, status=status.HTTP_200_OK)
        rotated = response.data.pop("refresh", None)
        if rotated:
            set_refresh_cookie(response, rotated)
        return response


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CSRFView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(responses={204: None})
    def get(self, request, *args, **kwargs):
        return Response(status=status.HTTP_204_NO_CONTENT)


@method_decorator(csrf_protect, name="dispatch")
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=None, responses={205: None})
    def post(self, request, *args, **kwargs):
        response = Response(status=status.HTTP_205_RESET_CONTENT)
        token = request.COOKIES.get(settings.AUTH_REFRESH_COOKIE)
        if token:
            try:
                RefreshToken(token).blacklist()
            except TokenError:
                pass
        delete_refresh_cookie(response)
        return response
