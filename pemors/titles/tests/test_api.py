from celery.states import SUCCESS
from django.test import Client, TestCase
from django.urls import reverse
from django_celery_results.models import TaskResult

from pemors.titles.models import UserTasks
from pemors.users.models import Profile, User


class FakeRequest:
    user = None


class ProgressTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="dummy", email="dummy@email.com")
        self.user.set_password("123")
        self.user.save()
        self.profile = Profile.objects.create(user=self.user)
        self.request = FakeRequest
        self.request.user = self.user
        self.client = Client()

    def test_only_authorized_users(self):
        response = self.client.get(reverse("titles_api:progress"))
        self.assertEqual(response.status_code, 403)

    def test_not_found(self):
        self.authenticate()
        response = self.client.get(reverse("titles_api:progress"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("status", response.json())
        self.assertEqual(response.json()["status"], "Not found")

    def test_in_progress(self):
        self.authenticate()
        task_result = TaskResult.objects.create()
        UserTasks.objects.create(user=self.user, task_result=task_result)
        response = self.client.get(reverse("titles_api:progress"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("status", response.json())
        self.assertEqual(response.json()["status"], "PENDING")

    def test_complete(self):
        self.authenticate()
        task_result = TaskResult.objects.create(status=SUCCESS)
        UserTasks.objects.create(user=self.user, task_result=task_result)
        response = self.client.get(reverse("titles_api:progress"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("status", response.json())
        self.assertEqual(response.json()["status"], SUCCESS)

    def authenticate(self):
        self.client.login(email=self.user.email, password="123")
