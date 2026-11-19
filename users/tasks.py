from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


@shared_task
def deactivate_inactive_users():
    """
    Блокирует пользователей, которые не заходили более месяца.
    """
    # Определяем дату "месяц назад" от текущего момента
    one_month_ago = timezone.now() - timedelta(days=30)

    # Находим активных пользователей, у которых last_login либо старше месяца, либо None
    inactive_users = User.objects.filter(is_active=True).filter(
        last_login__lt=one_month_ago
    ) | User.objects.filter(is_active=True, last_login__isnull=True)

    # Убираем дубликаты (если пользователь попал в оба условия)
    inactive_users = inactive_users.distinct()

    count = 0
    for user in inactive_users:
        user.is_active = False
        user.save(update_fields=["is_active"])
        count += 1

    return f"Заблокировано пользователей: {count}"
