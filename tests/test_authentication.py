from django.urls import reverse

from .base import BaseRemedialTestCase


class AuthenticationViewsTest(BaseRemedialTestCase):
    def test_login_success_redirects_to_dashboard(self):
        response = self.client.post(
            reverse("remedial:login"),
            data={"username": self.user.username, "password": "testpass123"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("remedial:dashboard"))

    def test_login_failure_renders_login_form(self):
        response = self.client.post(
            reverse("remedial:login"),
            data={"username": self.user.username, "password": "wrong"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<form method=\"post\">", html=False)
