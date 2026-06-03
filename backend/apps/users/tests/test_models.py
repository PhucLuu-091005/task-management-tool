import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()


@pytest.mark.django_db
def test_str_return_email_not_username(user):
    assert str(user) == user.email
    assert str(user) != user.username


@pytest.mark.django_db
def test_email_must_be_unique(user):
    with pytest.raises(IntegrityError):
        User.objects.create_user(
            email=user.email,
            username="different_user",
            password="random123214@",
        )


@pytest.mark.django_db
def test_username_must_be_unique(user):
    with pytest.raises(IntegrityError):
        User.objects.create_user(
            email="different@email.com",
            username=user.username,
            password="random123214@",
        )
