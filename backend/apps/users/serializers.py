from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from apps.users.constants import (
    EMAIL_UNIQUE_ERROR_MESSAGE,
    USERNAME_CONTENT_ERROR_MESSAGE,
    USERNAME_UNIQUE_ERROR_MESSAGE,
)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "username", "first_name", "last_name"]


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[
            UniqueValidator(queryset=User.objects.all(), message=EMAIL_UNIQUE_ERROR_MESSAGE)
        ]
    )
    username = serializers.CharField(
        validators=[
            UniqueValidator(queryset=User.objects.all(), message=USERNAME_UNIQUE_ERROR_MESSAGE)
        ]
    )
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)

    class Meta:
        model = User
        fields = ["email", "username", "password", "first_name", "last_name"]

    def validate_email(self, value: str) -> str:
        # Actual emails are case-insensitive, so we must protect against that
        return value.lower()

    def validate_username(self, value: str) -> str:
        if not value.isalnum():
            raise serializers.ValidationError(USERNAME_CONTENT_ERROR_MESSAGE)
        return value

    def validate(self, data: dict) -> dict:
        password = data.pop("password")
        # Build an unsaved User so UserAttributeSimilarityValidator can compare
        # the password against username/email/etc.
        user = User(**data)
        try:
            validate_password(
                password=password,
                user=user,
            )
        except DjangoValidationError as exc:
            # Make a dict so form binds as field error
            raise serializers.ValidationError({"password": list(exc.messages)}) from exc
        data["password"] = password
        return data

    def create(self, validated_data: dict) -> User:
        # Default fields (is_staff/is_superuser) are set here, password also hashed here
        try:
            return User.objects.create_user(**validated_data)
        except IntegrityError as exc:
            # Guard for case where 2 concurrent register come at a time
            # so the failed don't fire raw error to FE
            error_message = str(exc)
            if "email" in error_message:
                raise serializers.ValidationError({"email": EMAIL_UNIQUE_ERROR_MESSAGE}) from exc
            if "username" in error_message:
                raise serializers.ValidationError(
                    {"username": USERNAME_UNIQUE_ERROR_MESSAGE}
                ) from exc
            # Any other error, pop up to report, do not hide it here
            raise
