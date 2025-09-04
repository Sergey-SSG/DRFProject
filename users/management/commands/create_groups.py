from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management import BaseCommand

from materials.models import Course, Lesson


class Command(BaseCommand):
    help = "Создать группу модераторов с правами доступа"

    def handle(self, *args, **options):
        # Создаем группу модераторов
        moderators_group, created = Group.objects.get_or_create(name="moderators")

        # Добавляем права для модераторов
        course_content_type = ContentType.objects.get_for_model(Course)
        lesson_content_type = ContentType.objects.get_for_model(Lesson)

        # Права для курсов: просмотр и изменение, но не создание и удаление
        moderators_group.permissions.add(
            Permission.objects.get(
                codename="view_course", content_type=course_content_type
            ),
            Permission.objects.get(
                codename="change_course", content_type=course_content_type
            ),
            Permission.objects.get(
                codename="view_lesson", content_type=lesson_content_type
            ),
            Permission.objects.get(
                codename="change_lesson", content_type=lesson_content_type
            ),
        )

        self.stdout.write(self.style.SUCCESS("Группа модераторов успешно создана"))
