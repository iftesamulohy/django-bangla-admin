from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class AdminShellTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser(
            "admin", "a@example.com", "pw"
        )

    def setUp(self):
        self.client.force_login(self.user)

    def test_dashboard_renders_shell_and_widgets(self):
        r = self.client.get(reverse("bangla_admin:index"))
        self.assertEqual(r.status_code, 200)
        body = r.content.decode()
        self.assertIn("ba-shell", body)
        self.assertIn("ba-sidebar", body)
        self.assertIn("ba-grid", body)
        self.assertIn("ba-chart-sales", body)

    def test_htmx_strips_shell(self):
        r = self.client.get(
            reverse("bangla_admin:auth_user_changelist"),
            headers={"HX-Request": "true"},
        )
        self.assertEqual(r.status_code, 200)
        body = r.content.decode()
        self.assertNotIn("ba-shell", body)
        self.assertNotIn("<!--ba:content:start-->", body)

    def test_non_htmx_keeps_shell(self):
        r = self.client.get(reverse("bangla_admin:auth_user_changelist"))
        self.assertIn("ba-shell", r.content.decode())

    def test_chart_data_json(self):
        r = self.client.get(reverse("bangla_admin:ba_chart_data") + "?metric=sales")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn("labels", data)
        self.assertIn("datasets", data)
        self.assertEqual(len(data["labels"]), 30)

    def test_language_switch_sets_cookie(self):
        r = self.client.get(
            reverse("bangla_admin:ba_set_language") + "?lang=en",
            headers={"HX-Request": "true"},
        )
        self.assertEqual(r.status_code, 204)
        self.assertEqual(r.headers.get("HX-Refresh"), "true")
        self.assertIn("django_language", r.cookies)


class LoginThemeTests(TestCase):
    def test_login_page_is_themed_standalone(self):
        r = self.client.get(reverse("bangla_admin:login"))
        self.assertEqual(r.status_code, 200)
        body = r.content.decode()
        self.assertIn("data-ba-theme", body)
        self.assertNotIn("ba-shell", body)  # no sidebar for anonymous
