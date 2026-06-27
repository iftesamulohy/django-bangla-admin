from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

CHARTS = [
    {
        "id": "users_by_staff",
        "kind": "doughnut",
        "title": {"bn": "স্টাফ", "en": "By Staff"},
        "model": "auth.User",
        "group_by": "is_staff",
        "aggregate": "count",
    },
]

STAT_CARDS = [
    {"label": {"en": "Staff"}, "model": "auth.User", "aggregate": "count",
     "filters": {"is_staff": True}, "icon": "shield"},
]


class ConfigChartResolverTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        User.objects.create_superuser("admin", "a@example.com", "pw")
        User.objects.create_user("u1", "u1@example.com", "pw")
        User.objects.create_user("u2", "u2@example.com", "pw")

    def _request(self):
        from django.test import RequestFactory
        return RequestFactory().get("/admin/")

    @override_settings(BANGLA_ADMIN={"charts": CHARTS})
    def test_group_by_count(self):
        from django_bangla_admin.dashboard.data import resolve_config_chart

        data = resolve_config_chart("users_by_staff", self._request())
        self.assertEqual(set(data["labels"]), {"True", "False"})
        self.assertEqual(sum(data["datasets"][0]["data"]), 3)

    @override_settings(BANGLA_ADMIN={"charts": CHARTS})
    def test_unknown_chart_returns_empty(self):
        from django_bangla_admin.dashboard.data import resolve_config_chart

        self.assertEqual(
            resolve_config_chart("nope", self._request()),
            {"labels": [], "datasets": []},
        )

    @override_settings(BANGLA_ADMIN={"stat_cards": STAT_CARDS})
    def test_stat_card_with_filter(self):
        from django_bangla_admin.dashboard.data import resolve_stat_card

        value = resolve_stat_card(STAT_CARDS[0], self._request())
        self.assertEqual(value, 1)  # only the superuser is staff

    def test_decimal_coerced_to_float(self):
        from django_bangla_admin.dashboard.data import _to_number

        self.assertEqual(_to_number(Decimal("12.50")), 12.5)
        # Whole values are returned as int so KPIs don't show a trailing ".0".
        self.assertEqual(_to_number(Decimal("3")), 3)
        self.assertIsInstance(_to_number(Decimal("3")), int)
        self.assertEqual(_to_number(None), 0)


class ConfigChartViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        get_user_model().objects.create_superuser("admin", "a@example.com", "pw")

    @override_settings(BANGLA_ADMIN={"charts": CHARTS})
    def test_chart_data_endpoint_resolves_config(self):
        self.client.force_login(get_user_model().objects.get(username="admin"))
        from django.urls import reverse

        r = self.client.get(reverse("bangla_admin:ba_chart_data") + "?chart=users_by_staff")
        self.assertEqual(r.status_code, 200)
        self.assertIn("labels", r.json())
