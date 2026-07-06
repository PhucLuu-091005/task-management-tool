from django.urls import path

from apps.users.views import (
    CookieTokenObtainPairView,
    CookieTokenRefreshView,
    CSRFView,
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
    path("token/refresh/", CookieTokenRefreshView.as_view(), name="token_refresh"),
    path("csrf/", CSRFView.as_view(), name="csrf"),
    path("profile/", ProfileView.as_view(), name="profile"),
]
