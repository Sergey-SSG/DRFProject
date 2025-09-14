from rest_framework import serializers

from .models import Course, Lesson
from .validators import validate_youtube_only


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Lesson.objects.all(),
                fields=["title", "course"],
                message="Урок с таким названием уже существует в этом курсе",
            )
        ]

    def validate_video_link(self, value):
        """Валидация ссылки на видео."""
        return validate_youtube_only(value)

    def validate_description(self, value):
        """Валидация описания на наличие запрещенных ссылок."""
        if value:
            # Простая проверка на наличие http/https ссылок не на YouTube
            import re

            urls = re.findall(r'https?://[^\s<>"]+', value)
            for url in urls:
                validate_youtube_only(url)
        return value


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = "__all__"

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    def validate_description(self, value):
        """Валидация описания курса на наличие запрещенных ссылок."""
        if value:
            import re

            urls = re.findall(r'https?://[^\s<>"]+', value)
            for url in urls:
                validate_youtube_only(url)
        return value

    def get_is_subscribed(self, obj):
        """Проверяет, подписан ли текущий пользователь на курс."""
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.subscribers.filter(id=request.user.id).exists()
        return False
