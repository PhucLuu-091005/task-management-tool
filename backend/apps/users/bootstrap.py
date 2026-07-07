import os

from django.contrib.auth.hashers import make_password


def seed_admin_from_env(User, *, env=None):
    """Create or promote an app admin from environment variables.

    Idempotent: an existing user with the same username is promoted and has its
    password reset. Returns None (a no-op) when the credentials are absent, so
    deploys without the env vars set do nothing instead of failing.
    """
    env = os.environ if env is None else env
    username = env.get("INITIAL_ADMIN_USERNAME")
    password = env.get("INITIAL_ADMIN_PASSWORD")
    if not (username and password):
        return None

    email = env.get("INITIAL_ADMIN_EMAIL", f"{username}@example.com")
    user, _ = User.objects.update_or_create(
        username=username,
        defaults={
            "email": email,
            "is_admin": True,
            "is_active": True,
            "password": make_password(password),
        },
    )
    return user
