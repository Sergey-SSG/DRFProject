from django.urls import path

from .views import PaymentListAPIView, UserProfileUpdateAPIView

app_name = "users"

urlpatterns = [
    path(
        "profile/<int:pk>/update/",
        UserProfileUpdateAPIView.as_view(),
        name="user-profile-update",
    ),
    path(
        "profile/<int:pk>/update/",
        UserProfileUpdateAPIView.as_view(),
        name="user-profile-update",
    ),
    path("payments/", PaymentListAPIView.as_view(), name="payment-list"),
]
