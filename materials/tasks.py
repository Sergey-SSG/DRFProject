from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from materials.models import Course, Subscription


@shared_task
def send_course_update_notification(course_id):
    """
    Отправляет уведомления об обновлении курса подписанным пользователям
    """
    try:
        course = Course.objects.get(id=course_id)
        subscriptions = Subscription.objects.filter(course=course)

        for subscription in subscriptions:
            send_mail(
                subject=f"Обновление курса: {course.title}",
                message=f'Курс "{course.title}" был обновлен. Проверьте новые материалы!',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[subscription.user.email],
                fail_silently=False,
            )

        return f"Уведомления отправлены для курса {course.title}"

    except Course.DoesNotExist:
        return "Курс не найден"


@shared_task
def send_lesson_update_notification(course_id, lesson_title):
    """
    Отправляет уведомления об обновлении урока подписанным пользователям
    с проверкой времени последнего обновления курса
    """
    try:
        course = Course.objects.get(id=course_id)

        # Проверка: отправляем уведомление только если курс не обновлялся более 4 часов
        four_hours_ago = timezone.now() - timedelta(hours=4)
        if course.updated_at > four_hours_ago:
            return "Курс обновлялся менее 4 часов назад, уведомление не отправлено"

        subscriptions = Subscription.objects.filter(course=course)

        for subscription in subscriptions:
            send_mail(
                subject=f"Новый урок в курсе: {course.title}",
                message=f'В курсе "{course.title}" добавлен новый урок: "{lesson_title}"',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[subscription.user.email],
                fail_silently=False,
            )

        return f"Уведомления отправлены для урока {lesson_title} в курсе {course.title}"

    except Course.DoesNotExist:
        return "Курс не найден"
