from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from .forms import PostForm
from .models import Category
from .views import SecureUserCreationForm


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

    def test_staff_can_create_category(self):
        self.client.login(username="editor", password="editorpass")
        response = self.client.post(
            reverse("blog:category_create"),
            {"name": "Technology", "slug": "technology"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Category.objects.filter(slug="technology").exists())

    def test_signup_creates_new_user_and_logs_in(self):
        response = self.client.post(
            reverse("blog:signup"),
            {"username": "newreader", "password1": "StrongPass123!", "password2": "StrongPass123!"},
            follow=True,
        )
        self.assertRedirects(response, reverse("blog:post_list"))
        self.assertTrue(get_user_model().objects.filter(username="newreader").exists())

    def test_post_form_uses_draft_status_dropdown(self):
        form = PostForm()
        self.assertIn("status", form.fields)
        self.assertNotIn("tags", form.fields)
        self.assertEqual(form.fields["status"].initial, "draft")

    def test_signup_form_uses_styled_inputs(self):
        form = SecureUserCreationForm()
        self.assertIn("form-input", form.fields["username"].widget.attrs.get("class", ""))
        self.assertIn("form-input", form.fields["password1"].widget.attrs.get("class", ""))
        self.assertIn("form-input", form.fields["password2"].widget.attrs.get("class", ""))
