from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.users.views import (
    CookieTokenObtainPairView,
    LogoutView,
    ProfileView,
    RegisterView,
    UserListView,
)

urlpatterns = [
    path("", UserListView.as_view(), name="user-list"),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", CookieTokenObtainPairView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/refresh", TokenRefreshView.as_view(), name="token_refresh"),
    path("profile/", ProfileView.as_view(), name="profile"),
]
