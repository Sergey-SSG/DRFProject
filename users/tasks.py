from datetime import timedelta

from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


@shared_task
def check_inactive_users():
    """
    Проверяет пользователей, которые не заходили более месяца,
    и блокирует их (is_active=False) с отправкой уведомления
    """
    one_month_ago = timezone.now() - timedelta(days=30)

    inactive_users = User.objects.filter(last_login__lt=one_month_ago, is_active=True)

    for user in inactive_users:
        user.is_active = False
        user.save()
        # Отправляем уведомление
        send_deactivation_notification.delay(user.id)

    return f"Заблокировано {inactive_users.count()} неактивных пользователей"


@shared_task
def send_deactivation_notification(user_id):
    """
    Отправляет уведомление пользователю о блокировке аккаунта
    """
    try:
        user = User.objects.get(id=user_id)

        from django.conf import settings
        from django.core.mail import send_mail

        send_mail(
            subject="Ваш аккаунт был заблокирован",
            message="Ваш аккаунт был заблокирован из-за отсутствия активности более 30 дней.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return f"Уведомление отправлено пользователю {user.email}"

    except User.DoesNotExist:
        return "Пользователь не найден"
