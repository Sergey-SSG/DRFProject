from django.core.management.base import BaseCommand

from materials.models import Course, Lesson
from users.models import Payment, User


class Command(BaseCommand):
    help = "Load initial payment data"

    def handle(self, *args, **options):
        # Создаем тестовые платежи
        user1 = User.objects.get(
            email="admin@example.com"
        )
        user2 = User.objects.first()  # Первый пользователь

        course1 = Course.objects.first()
        course2 = Course.objects.last()
        lesson1 = Lesson.objects.first()

        Payment.objects.create(
            user=user1, paid_course=course1, amount=10000.00, payment_method="transfer"
        )

        Payment.objects.create(
            user=user1, paid_lesson=lesson1, amount=2000.00, payment_method="cash"
        )

        Payment.objects.create(
            user=user2, paid_course=course2, amount=15000.00, payment_method="transfer"
        )

        self.stdout.write(self.style.SUCCESS("Successfully loaded payment data"))
