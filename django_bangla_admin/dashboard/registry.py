"""Dashboard resolution: load the configured dashboard class."""

from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string

from ..conf import ba_conf

_INSTANCE = None


def get_dashboard():
    """Instantiate (and cache) the dashboard named in ``BANGLA_ADMIN['dashboard']``."""
    global _INSTANCE
    if _INSTANCE is not None:
        return _INSTANCE
    dotted = ba_conf("dashboard", "django_bangla_admin.dashboard.default.DefaultDashboard")
    try:
        cls = import_string(dotted)
    except ImportError as exc:
        raise ImproperlyConfigured(
            f"BANGLA_ADMIN['dashboard'] could not be imported: {dotted!r}"
        ) from exc
    _INSTANCE = cls()
    return _INSTANCE


def reset():
    """Clear the cached dashboard (used in tests / after setting changes)."""
    global _INSTANCE
    _INSTANCE = None
