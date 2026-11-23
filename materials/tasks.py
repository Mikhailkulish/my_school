from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from materials.models import Subscription


@shared_task
def send_course_update_email(course_id, course_title):
    """
    Отправляет письмо всем подписчикам курса при его обновлении.
    """
    # Получаем всех подписчиков курса
    subscriptions = Subscription.objects.filter(course_id=course_id).select_related("user")

    if not subscriptions.exists():
        return f"Нет подписчиков у курса {course_id}"

    # Формируем список email-адресов подписчиков
    emails = [sub.user.email for sub in subscriptions if sub.user.email]

    if not emails:
        return f"У подписчиков курса {course_id} нет email-адресов"

    # Тема и текст письма
    subject = f"Обновление курса: {course_title}"
    message = (
        f"Здравствуйте!\n\n"
        f"Курс «{course_title}» был обновлён. "
        f"Проверьте новые материалы в вашем личном кабинете.\n\n"
        f"С уважением,\n"
        f"Команда my_school"
    )

    # Отправляем письма (используем BCC, чтобы не раскрывать адреса)
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=emails,
        fail_silently=False,
    )

    return f"Письма отправлены {len(emails)} подписчикам курса {course_id}"
