from django.contrib.auth import get_user_model
from django.db.models import prefetch_related_objects
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.constants import MISSING_REFRESH_TOKEN_ERROR_MESSAGE, TOKEN_INVALID_ERROR_MESSAGE
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


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            token = RefreshToken(request.data["refresh"])
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except KeyError:
            return Response(
                {"refresh": MISSING_REFRESH_TOKEN_ERROR_MESSAGE}, status=status.HTTP_400_BAD_REQUEST
            )
        except TokenError:
            return Response(
                {"refresh": TOKEN_INVALID_ERROR_MESSAGE}, status=status.HTTP_400_BAD_REQUEST
            )
