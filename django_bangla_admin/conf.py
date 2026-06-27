"""Lazy, cached accessor for the merged BANGLA_ADMIN configuration.

Usage::

    from django_bangla_admin.conf import ba_conf
    ba_conf("theme")            # -> "dark"
    ba_conf("menu", default=[]) # -> resolved value or default
    ba_conf.as_dict()           # -> full merged dict

The merged config is the host project's ``settings.BANGLA_ADMIN`` deep-merged
over :data:`django_bangla_admin.settings.DEFAULTS`.
"""

import copy

from django.conf import settings
from django.dispatch import receiver
from django.test.signals import setting_changed

from .settings import DEFAULTS


def _deep_merge(base, override):
    """Recursively merge ``override`` onto a copy of ``base``."""
    result = copy.deepcopy(base)
    for key, value in (override or {}).items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(value, dict)
        ):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


class _Conf:
    """Callable config accessor with a memoized merged dict."""

    _cache = None

    def reload(self):
        user = getattr(settings, "BANGLA_ADMIN", {}) or {}
        if not isinstance(user, dict):
            raise TypeError("BANGLA_ADMIN setting must be a dict.")
        self._cache = _deep_merge(DEFAULTS, user)
        return self._cache

    def as_dict(self):
        if self._cache is None:
            self.reload()
        return self._cache

    def __call__(self, key, default=None):
        data = self.as_dict()
        return data.get(key, default)


ba_conf = _Conf()


@receiver(setting_changed)
def _reload_on_setting_change(sender, setting, **kwargs):
    # Keep config in sync when tests use override_settings(BANGLA_ADMIN=...).
    if setting == "BANGLA_ADMIN":
        ba_conf.reload()
