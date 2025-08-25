from django.urls import path

from .views import UserProfileUpdateAPIView

app_name = "users"

urlpatterns = [
    path(
        "profile/<int:pk>/update/",
        UserProfileUpdateAPIView.as_view(),
        name="user-profile-update",
    ),
]
