from rest_framework import generics, permissions

from .models import User
from .serializers import UserProfileSerializer


class UserProfileUpdateAPIView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
