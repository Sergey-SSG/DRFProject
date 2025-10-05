from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (CustomTokenObtainPairView, PaymentListAPIView,
                    UserDestroyAPIView, UserListAPIView,
                    UserProfileUpdateAPIView, UserRegisterAPIView,
                    UserRetrieveAPIView, UserUpdateAPIView)

app_name = "users"

urlpatterns = [
    path("register/", UserRegisterAPIView.as_view(), name="user-register"),
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("", UserListAPIView.as_view(), name="user-list"),
    path("<int:pk>/", UserRetrieveAPIView.as_view(), name="user-detail"),
    path("<int:pk>/update/", UserUpdateAPIView.as_view(), name="user-update"),
    path("<int:pk>/delete/", UserDestroyAPIView.as_view(), name="user-delete"),
    path(
        "profile/<int:pk>/update/",
        UserProfileUpdateAPIView.as_view(),
        name="user-profile-update",
    ),
    path("payments/", PaymentListAPIView.as_view(), name="payment-list"),
]
