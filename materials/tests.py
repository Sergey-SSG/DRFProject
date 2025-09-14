from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from .models import Course, Lesson, Subscription

User = get_user_model()


class LessonTestCase(APITestCase):
    def setUp(self):
        """Настройка тестовых данных"""
        self.client = APIClient()

        # Создание 2-х пользователей
        self.user = User.objects.create(
            email="testuser@example.com", first_name="Test", last_name="User"
        )
        self.user.set_password("testpass123")
        self.user.save()

        self.moderator = User.objects.create(
            email="moderator@example.com", first_name="Moderator", last_name="User"
        )
        self.moderator.set_password("modpass123")
        self.moderator.save()

        # Создание группы модераторов, добавляем пользователя
        moderators_group = Group.objects.create(name="moderators")
        self.moderator.groups.add(moderators_group)

        # Создание курса
        self.course = Course.objects.create(
            title="Test Course", description="Test Description", owner=self.user
        )

        # Создание урока
        self.lesson = Lesson.objects.create(
            title="Test Lesson",
            description="Test Lesson Description",
            course=self.course,
            video_link="https://www.youtube.com/watch?v=test",
            owner=self.user,
        )

    def test_lesson_create(self):
        """Тест создания урока"""
        self.client.force_authenticate(user=self.user)

        data = {
            "title": "New Lesson",
            "description": "New Lesson Description",
            "course": self.course.id,
            "video_link": "https://www.youtube.com/watch?v=new",
        }

        response = self.client.post(reverse("materials:lesson-create"), data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)

    def test_lesson_create_invalid_link(self):
        """Тест создания урока с невалидной ссылкой"""
        self.client.force_authenticate(user=self.user)

        data = {
            "title": "Invalid Lesson",
            "description": "Invalid Lesson Description",
            "course": self.course.id,
            "video_link": "https://vimeo.com/test",  # Не YouTube!
        }

        response = self.client.post(reverse("materials:lesson-create"), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("video_link", response.data)

    def test_moderator_cannot_create_lesson(self):
        """Тест, что модератор не может создавать уроки"""
        self.client.force_authenticate(user=self.moderator)

        data = {
            "title": "Moderator Lesson",
            "description": "Moderator Lesson Description",
            "course": self.course.id,
            "video_link": "https://www.youtube.com/watch?v=mod",
        }

        response = self.client.post(reverse("materials:lesson-create"), data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class SubscriptionTestCase(APITestCase):
    def setUp(self):
        """Настройка тестовых данных для подписок"""
        self.client = APIClient()

        # Создание пользователя
        self.user = User.objects.create(
            email="testuser@example.com", first_name="Test", last_name="User"
        )
        self.user.set_password("testpass123")
        self.user.save()

        # Создание курса
        self.course = Course.objects.create(
            title="Test Course for Subscription",
            description="Test Description",
            owner=self.user,
        )

    def test_subscription_create(self):
        """Тест создания подписки"""
        self.client.force_authenticate(user=self.user)

        data = {"course_id": self.course.id}

        response = self.client.post(reverse("materials:subscription"), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Подписка добавлена")
        self.assertTrue(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

    def test_subscription_remove(self):
        """Тест удаления подписки"""
        # Создание подписки
        Subscription.objects.create(user=self.user, course=self.course)

        self.client.force_authenticate(user=self.user)

        data = {"course_id": self.course.id}

        response = self.client.post(reverse("materials:subscription"), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Подписка удалена")
        self.assertFalse(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )


class CourseViewSetTestCase(APITestCase):
    def setUp(self):
        """Тесты для CourseViewSet"""
        self.client = APIClient()

        # Создание пользователя
        self.user = User.objects.create(
            email="courseuser@example.com", first_name="Course", last_name="User"
        )
        self.user.set_password("testpass123")
        self.user.save()

        # Создание курса
        self.course = Course.objects.create(
            title="Test Course ViewSet", description="Test Description", owner=self.user
        )

    def test_course_list(self):
        """Тест получения списка курсов"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse("materials:course-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)  # С пагинацией

    def test_course_create(self):
        """Тест создания курса"""
        self.client.force_authenticate(user=self.user)

        data = {"title": "New Course", "description": "New Course Description"}

        response = self.client.post(reverse("materials:course-list"), data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.count(), 2)
