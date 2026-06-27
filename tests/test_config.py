from django.test import SimpleTestCase, override_settings

from django_bangla_admin.conf import _deep_merge, ba_conf
from django_bangla_admin.settings import DEFAULTS


class DeepMergeTests(SimpleTestCase):
    def test_merges_nested_dicts(self):
        base = {"a": 1, "b": {"x": 1, "y": 2}}
        out = _deep_merge(base, {"b": {"y": 9, "z": 3}})
        self.assertEqual(out, {"a": 1, "b": {"x": 1, "y": 9, "z": 3}})

    def test_does_not_mutate_base(self):
        base = {"b": {"x": 1}}
        _deep_merge(base, {"b": {"x": 2}})
        self.assertEqual(base, {"b": {"x": 1}})


class ConfAccessorTests(SimpleTestCase):
    def test_defaults_present(self):
        self.assertEqual(ba_conf("theme"), DEFAULTS["theme"])

    @override_settings(BANGLA_ADMIN={"theme": "light", "site_title": "X"})
    def test_user_override_wins(self):
        self.assertEqual(ba_conf("theme"), "light")
        self.assertEqual(ba_conf("site_title"), "X")
        # Unspecified keys keep defaults.
        self.assertEqual(ba_conf("swap_target"), DEFAULTS["swap_target"])

    @override_settings(BANGLA_ADMIN={"icons": {"shop.Order": "cart"}})
    def test_nested_dict_deep_merged(self):
        icons = ba_conf("icons")
        self.assertEqual(icons["shop.Order"], "cart")
        self.assertEqual(icons["auth.User"], DEFAULTS["icons"]["auth.User"])
