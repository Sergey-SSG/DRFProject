from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Payment, User
from .permissions import IsModerator, IsOwner, IsOwnerOrModerator
from .serializers import (CustomTokenObtainPairSerializer,
                          PaymentHistorySerializer, PaymentSerializer,
                          UserProfileSerializer, UserPublicSerializer,
                          UserRegisterSerializer, UserSerializer)


class CustomTokenObtainPairView(TokenObtainPairView):
    """Кастомный view для получения JWT токенов"""

    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]


class UserRegisterAPIView(generics.CreateAPIView):
    """Регистрация нового пользователя"""

    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]


class UserListAPIView(generics.ListAPIView):
    """Получение списка всех пользователей (только для модераторов)"""

    queryset = User.objects.all()
    serializer_class = UserPublicSerializer
    permission_classes = [permissions.IsAuthenticated, IsModerator]


class UserRetrieveAPIView(generics.RetrieveAPIView):
    """Получение информации о пользователе"""

    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if getattr(self, 'swagger_fake_view', False):
            return UserPublicSerializer

        user_id = self.kwargs.get('pk')
        if self.request.user.is_authenticated and user_id == str(self.request.user.pk):
            return UserSerializer

        return UserPublicSerializer


class UserUpdateAPIView(generics.UpdateAPIView):
    """Обновление информации о пользователе"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]


class UserDestroyAPIView(generics.DestroyAPIView):
    """Удаление пользователя"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]


class UserProfileUpdateAPIView(generics.UpdateAPIView):
    """Обновление профиля текущего пользователя"""

    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserProfileRetrieveAPIView(generics.RetrieveAPIView):
    """Получение профиля текущего пользователя"""

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class PaymentListAPIView(generics.ListAPIView):
    """Получение списка платежей с фильтрацией"""

    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["paid_course", "paid_lesson", "payment_method"]
    ordering_fields = ["payment_date"]

    def get_queryset(self):
        """Показываем только платежи текущего пользователя, если не модератор"""
        if self.request.user.groups.filter(name="moderators").exists():
            return Payment.objects.all()
        return Payment.objects.filter(user=self.request.user)


class PaymentCreateAPIView(generics.CreateAPIView):
    """Создание нового платежа"""

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PaymentRetrieveAPIView(generics.RetrieveAPIView):
    """Получение информации о платеже"""

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrModerator]


class PaymentUpdateAPIView(generics.UpdateAPIView):
    """Обновление информации о платеже"""

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrModerator]


class PaymentDestroyAPIView(generics.DestroyAPIView):
    """Удаление платежа"""

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrModerator]


class UserPaymentHistoryAPIView(generics.ListAPIView):
    """История платежей пользователя"""

    serializer_class = PaymentHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs.get("pk")
        if (
                self.request.user.id == user_id
                or self.request.user.groups.filter(name="moderators").exists()
        ):
            return Payment.objects.filter(user_id=user_id)
        return Payment.objects.none()
