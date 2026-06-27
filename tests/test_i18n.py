from django.test import SimpleTestCase, override_settings
from django.utils import translation

from django_bangla_admin.templatetags.ba_i18n import bn_number, resolve_label


class LabelResolveTests(SimpleTestCase):
    def test_plain_string_passthrough(self):
        self.assertEqual(resolve_label("Hello"), "Hello")

    def test_dict_resolves_to_active_language(self):
        label = {"bn": "পণ্য", "en": "Products"}
        with translation.override("bn"):
            self.assertEqual(resolve_label(label), "পণ্য")
        with translation.override("en"):
            self.assertEqual(resolve_label(label), "Products")

    def test_dict_falls_back_to_en(self):
        with translation.override("bn"):
            self.assertEqual(resolve_label({"en": "Only EN"}), "Only EN")


class BanglaNumeralTests(SimpleTestCase):
    def test_converts_when_bangla(self):
        with translation.override("bn"):
            self.assertEqual(bn_number(1234), "১২৩৪")

    def test_identity_when_english(self):
        # Non-Bangla returns the value unchanged (str() happens at render time).
        with translation.override("en"):
            self.assertEqual(bn_number(1234), 1234)

    @override_settings(BANGLA_ADMIN={"bangla_numerals": False})
    def test_disabled_by_config(self):
        with translation.override("bn"):
            self.assertEqual(bn_number(1234), 1234)
