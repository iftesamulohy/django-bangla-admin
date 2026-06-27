"""Site registration helpers and the public URLConf entry point.

End users wire the themed admin with three lines::

    # urls.py
    from django_bangla_admin.sites import urls as ba_urls
    urlpatterns = [path("admin/", ba_urls)]

Importing ``urls`` autodiscovers admin modules and mirrors every model
registered on the default ``django.contrib.admin.site`` onto the themed
:data:`site`, so existing ``@admin.register`` / ``admin.site.register`` calls
work unchanged. ``urls`` resolves to a standard ``(patterns, app_name, name)``
tuple, exactly like ``django.contrib.admin.site.urls``.
"""

from django.contrib import admin as django_admin
from django.utils.module_loading import autodiscover_modules

from .admin import site


def mirror_default_registry():
    """Copy registrations from the default admin site onto the themed site."""
    default_site = django_admin.site
    for model, model_admin in default_site._registry.items():
        if site.is_registered(model):
            continue
        # Re-instantiate the ModelAdmin class against our site so reverse()
        # and admin_view permissions resolve to the themed namespace.
        site.register(model, model_admin.__class__)


def autodiscover():
    """Run Django admin autodiscovery, then mirror the registry."""
    autodiscover_modules("admin", register_to=django_admin.site)
    mirror_default_registry()


def get_urls():
    """Return the themed site's include-compatible URL tuple."""
    autodiscover()
    return site.urls


def __getattr__(name):
    # PEP 562: compute ``urls`` lazily so autodiscovery runs at URLConf load,
    # by which point all apps are ready and the default admin is populated.
    if name == "urls":
        return get_urls()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
