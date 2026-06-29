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
        # Auto mode returns a single unlabeled section whose items are
        # collapsible app groups (each app -> model children).
        self.assertEqual(len(menu), 1)
        self.assertIsNone(menu[0]["section"])
        apps = menu[0]["items"]
        # Auth app should appear as a parent node with model children.
        auth = next(
            (a for a in apps if "auth" in str(a["label"]).lower()), None
        )
        self.assertIsNotNone(auth)
        # Auth registers User + Group, so the parent must carry child links.
        self.assertGreaterEqual(len(auth["children"]), 1)
        self.assertTrue(all(c["url"] for c in auth["children"]))

    @override_settings(BANGLA_ADMIN={"show_sidebar": False})
    def test_hidden_sidebar_returns_empty(self):
        self.assertEqual(build_menu(self._request(), site), [])
