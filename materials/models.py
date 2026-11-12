from django.db import models

from config import settings


class Course(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name="Название курса",
        help_text="Укажите название курса",
    )
    preview_image = models.ImageField(
        upload_to="materials/courses/photo",
        verbose_name="Превью курса",
        help_text="Загрузите превью курса",
        blank=True,
        null=True,
    )
    description = models.TextField(
        verbose_name="Описание курса",
        help_text="Введите описание курса",
        blank=True,
        null=True,
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="courses",
        verbose_name="Владелец",
        null=True,
        blank=True,
    )
    video_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="Ссылка на видео",
        help_text="Укажите ссылку на видео (только YouTube)",
    )

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"


class Lesson(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name="Название урока",
        help_text="Укажите название урока",
    )
    preview_image = models.ImageField(
        upload_to="materials/lessons/photo",
        verbose_name="Превью урока",
        help_text="Загрузите превью урока",
        blank=True,
        null=True,
    )
    description = models.TextField(
        verbose_name="Описание урока",
        help_text="Введите описание урока",
        blank=True,
        null=True,
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        help_text="Выберите курс урока",
        blank=True,
        null=True,
        related_name="lessons",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name="Владелец",
        null=True,
        blank=True,
    )
    video_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="Ссылка на видео",
        help_text="Укажите ссылку на видео (только YouTube)",
    )

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"


class Subscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="Пользователь",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="Курс",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        unique_together = ("user", "course")

    def __str__(self):
        return f"{self.user} → {self.course}"
