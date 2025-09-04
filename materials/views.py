from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions, viewsets

from users.permissions import IsModerator, IsOwnerOrModerator

from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с курсами"""

    queryset = Course.objects.all()
    serializer_class = CourseSerializer

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
