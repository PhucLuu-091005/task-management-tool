from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import prefetch_related_objects
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.users.constants import REFRESH_COOKIE_MISSING_ERROR_MESSAGE
from apps.users.cookies import delete_refresh_cookie, set_refresh_cookie
from apps.users.managers import MEMBERSHIPS_PREFETCH
from apps.users.permissions import IsAdmin
from apps.users.serializers import RegisterSerializer, UserSerializer

User = get_user_model()


class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *arg, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        prefetch_related_objects([user], MEMBERSHIPS_PREFETCH)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class UserListView(ListAPIView):
    queryset = User.objects.with_memberships()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]


class ProfileView(APIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        prefetch_related_objects([request.user], MEMBERSHIPS_PREFETCH)
        return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)


class CookieTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        refresh = response.data.pop("refresh", None)
        if refresh:
            set_refresh_cookie(response, refresh)
        return response


@method_decorator(csrf_protect, name="dispatch")
class CookieTokenRefreshView(TokenRefreshView):
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
