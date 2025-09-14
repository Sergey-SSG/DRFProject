from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Payment, User


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Кастомный сериализатор для JWT токенов с добавлением email в payload"""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        return token


class UserRegisterSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя"""

    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "password2",
            "first_name",
            "last_name",
            "phone",
            "city",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Поля пароля не совпали."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        password = validated_data.pop("password")

        # Создаем пользователя через модель
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        return user


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для полной информации о пользователе (для владельца)"""

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "city",
            "avatar",
            "date_joined",
        ]
        read_only_fields = ["id", "date_joined"]


class UserPublicSerializer(serializers.ModelSerializer):
    """Сериализатор для публичной информации о пользователе (для других пользователей)"""

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "city", "avatar"]
        read_only_fields = ["id", "email"]


class UserProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления профиля пользователя"""

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "city",
            "avatar",
            "date_joined",
        ]
        read_only_fields = ["id", "email", "date_joined"]


class PaymentSerializer(serializers.ModelSerializer):
    """Сериализатор для платежей"""

    class Meta:
        model = Payment
        fields = "__all__"


class PaymentHistorySerializer(serializers.ModelSerializer):
    """Сериализатор для истории платежей в профиле пользователя"""

    class Meta:
        model = Payment
        fields = [
            "payment_date",
            "paid_course",
            "paid_lesson",
            "amount",
            "payment_method",
        ]
