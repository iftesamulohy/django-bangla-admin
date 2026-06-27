from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase, override_settings

from django_bangla_admin.admin import site
from django_bangla_admin.menu import build_menu


class MenuBuilderTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser(
            "admin", "a@example.com", "pw"
        )

    def _request(self):
        rf = RequestFactory()
        req = rf.get("/admin/")
        req.user = self.user
        return req

    def test_manual_menu_sections_and_items(self):
        menu = build_menu(self._request(), site)
        # configured in tests/settings: one section "Main" with 2 items.
        self.assertTrue(menu)
        first = menu[0]
        self.assertIn("section", first)
        labels = [i["label"] for i in first["items"]]
        self.assertIn({"bn": "ড্যাশবোর্ড", "en": "Dashboard"}, labels)

    @override_settings(BANGLA_ADMIN={"menu": None})
    def test_auto_menu_from_registry(self):
        menu = build_menu(self._request(), site)
        # Auth app should appear with User/Group models.
        names = [s["section"] for s in menu]
        self.assertTrue(any("auth" in str(n).lower() or "Auth" in str(n) for n in names))

    @override_settings(BANGLA_ADMIN={"show_sidebar": False})
    def test_hidden_sidebar_returns_empty(self):
        self.assertEqual(build_menu(self._request(), site), [])
