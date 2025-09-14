from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from users.permissions import IsModerator, IsOwnerOrModerator

from .models import Course, Lesson, Subscription
from .paginators import CoursePagination, LessonPagination
from .serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с курсами"""

    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = CoursePagination

    def get_permissions(self):
        if self.action in ["create", "destroy"]:
            self.permission_classes = [permissions.IsAuthenticated, ~IsModerator]
        elif self.action in ["update", "partial_update"]:
            self.permission_classes = [permissions.IsAuthenticated, IsOwnerOrModerator]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        """Фильтруем курсы: модераторы видят все, обычные пользователи - только свои"""
        queryset = super().get_queryset()
        if not self.request.user.groups.filter(name="moderators").exists():
            queryset = queryset.filter(owner=self.request.user)
        return queryset


class LessonListAPIView(generics.ListAPIView):
    """Получение списка уроков с фильтрацией"""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = LessonPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["course"]
    ordering_fields = ["title"]

    def get_queryset(self):
        """Фильтруем уроки: модераторы видят все, обычные пользователи - только свои"""
        queryset = super().get_queryset()
        if not self.request.user.groups.filter(name="moderators").exists():
            queryset = queryset.filter(owner=self.request.user)
        return queryset


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    """Получение детальной информации об уроке"""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrModerator]


class LessonCreateAPIView(generics.CreateAPIView):
    """Создание нового урока"""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated, ~IsModerator]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonUpdateAPIView(generics.UpdateAPIView):
    """Обновление существующего урока"""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrModerator]


class LessonDestroyAPIView(generics.DestroyAPIView):
    """Удаление урока"""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrModerator]


class SubscriptionAPIView(APIView):
    """API View для управления подписками на курсы"""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get("course_id")

        if not course_id:
            return Response(
                {"error": "course_id обязателен"}, status=status.HTTP_400_BAD_REQUEST
            )

        course = get_object_or_404(Course, id=course_id)
        subscription = Subscription.objects.filter(user=user, course=course)

        if subscription.exists():
            subscription.delete()
            message = "Подписка удалена"
        else:
            Subscription.objects.create(user=user, course=course)
            message = "Подписка добавлена"

        return Response({"message": message}, status=status.HTTP_200_OK)
