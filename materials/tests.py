from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from materials.models import Course, Lesson, Subscription
from users.models import User


def create_test_user(email, password="pass123"):
    """Создаёт пользователя без использования create_user (обход бага UserManager)."""
    user = User.objects.create(email=email, is_active=True)
    user.set_password(password)
    user.save()
    return user


class LessonCRUDTestCase(APITestCase):
    def setUp(self):
        self.moders_group = Group.objects.create(name="moders")

        self.owner = create_test_user("owner@example.com")
        self.moderator = create_test_user("moderator@example.com")
        self.moderator.groups.add(self.moders_group)
        self.stranger = create_test_user("stranger@example.com")

        self.course = Course.objects.create(
            title="Test Course", description="Desc", owner=self.owner
        )
        self.lesson = Lesson.objects.create(
            title="Test Lesson",
            description="Desc",
            course=self.course,
            owner=self.owner,
        )

    # --- CREATE ---
    def test_owner_can_create_lesson(self):
        self.client.force_authenticate(user=self.owner)
        data = {
            "title": "New Lesson",
            "description": "New Desc",
            "course": self.course.id,
        }
        response = self.client.post(reverse("materials:lessons_create"), data)
        if response.status_code != 201:
            print("DEBUG 400:", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_moderator_cannot_create_lesson(self):
        self.client.force_authenticate(user=self.moderator)
        data = {"title": "New", "description": "D", "course": self.course.id}
        response = self.client.post(reverse("materials:lessons_create"), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --- READ ---
    def test_owner_can_retrieve_own_lesson(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(
            reverse("materials:lessons_retrieve", args=[self.lesson.id])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_stranger_cannot_retrieve_lesson(self):
        self.client.force_authenticate(user=self.stranger)
        response = self.client.get(
            reverse("materials:lessons_retrieve", args=[self.lesson.id])
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # --- UPDATE ---
    def test_owner_can_update_own_lesson(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(
            reverse("materials:lessons_update", args=[self.lesson.id]),
            {"title": "Updated"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_moderator_can_update_any_lesson(self):
        self.client.force_authenticate(user=self.moderator)
        response = self.client.patch(
            reverse("materials:lessons_update", args=[self.lesson.id]),
            {"title": "Moderated"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # --- DELETE ---
    def test_owner_can_delete_own_lesson(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(
            reverse("materials:lessons_delete", args=[self.lesson.id])
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_moderator_cannot_delete_lesson(self):
        self.client.force_authenticate(user=self.moderator)
        response = self.client.delete(
            reverse("materials:lessons_delete", args=[self.lesson.id])
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class SubscriptionTestCase(APITestCase):
    def setUp(self):
        self.user = create_test_user("testuser@example.com")
        self.course = Course.objects.create(
            title="Sub Course", description="Desc", owner=self.user
        )

    def test_subscribe_to_course(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            reverse("materials:subscriptions"), {"course_id": self.course.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "подписка добавлена")
        self.assertTrue(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

    def test_unsubscribe_from_course(self):
        Subscription.objects.create(user=self.user, course=self.course)
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            reverse("materials:subscriptions"), {"course_id": self.course.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "подписка удалена")
        self.assertFalse(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

    def test_subscription_flag_in_course_detail(self):
        Subscription.objects.create(user=self.user, course=self.course)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            reverse("materials:course-detail", args=[self.course.id])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_subscribed"])


class CourseTestCase(APITestCase):
    def setUp(self):
        self.moders_group = Group.objects.create(name="moders")

        self.owner = create_test_user("course_owner@example.com")
        self.moderator = create_test_user("course_moderator@example.com")
        self.moderator.groups.add(self.moders_group)
        self.stranger = create_test_user("course_stranger@example.com")

        self.course = Course.objects.create(
            title="Test Course", description="Desc", owner=self.owner
        )

    def test_stranger_cannot_update_course(self):
        self.client.force_authenticate(user=self.stranger)
        response = self.client.patch(
            reverse("materials:course-detail", args=[self.course.id]),
            {"title": "Чужое изменение"},
        )
        self.assertIn(
            response.status_code,
            (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND),
        )

    def test_anonymous_cannot_update_course(self):
        response = self.client.patch(
            reverse("materials:course-detail", args=[self.course.id]),
            {"title": "Без авторизации"},
        )
        self.assertIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )
