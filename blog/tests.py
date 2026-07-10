from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class BlogAuthFlowTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="reader", password="readerpass")
        self.staff_user = get_user_model().objects.create_user(username="editor", password="editorpass", is_staff=True)

    def test_homepage_is_public_for_anonymous_users(self):
        response = self.client.get(reverse("blog:post_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Latest posts")

    def test_user_login_redirects_non_staff_to_home(self):
        response = self.client.post(
            reverse("blog:login"),
            {"username": "reader", "password": "readerpass"},
            follow=True,
        )
        self.assertRedirects(response, reverse("blog:post_list"))

    def test_staff_login_redirects_to_dashboard(self):
        response = self.client.post(
            reverse("blog:login"),
            {"username": "editor", "password": "editorpass"},
            follow=True,
        )
        self.assertRedirects(response, reverse("blog:dashboard"))
