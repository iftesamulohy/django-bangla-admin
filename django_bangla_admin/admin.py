"""BanglaAdminSite — themed AdminSite with dashboard + chart-data endpoints.

Drop-in replacement for ``django.contrib.admin.site``. It reuses Django's
admin registry/permissions and only adds theming, a dashboard index, the
language-switch view, and JSON chart-data endpoints.
"""

from django.contrib.admin import AdminSite
from django.urls import path
from django.utils.translation import gettext_lazy as _

from .conf import ba_conf


class BanglaAdminSite(AdminSite):
    """A themed admin site for a Bangladeshi audience."""

    # Defaults; overridden per-request from BANGLA_ADMIN via each_context.
    site_title = ba_conf("site_title")
    site_header = ba_conf("site_header")
    index_title = _("Dashboard")
    enable_nav_sidebar = False  # we render our own sidebar

    def each_context(self, request):
        context = super().each_context(request)
        context.update(self._ba_context(request))
        return context

    def _ba_context(self, request):
        """Inject Bangla-admin specifics shared by every admin page."""
        from .menu import build_menu

        return {
            "ba": ba_conf.as_dict(),
            "ba_menu": build_menu(request, self),
        }

    def get_urls(self):
        from . import i18n, views

        custom = [
            path("ba/set-language/", self.admin_view(i18n.set_language), name="ba_set_language"),
            path("ba/chart-data/", self.admin_view(views.chart_data), name="ba_chart_data"),
        ]
        # Custom routes must precede the catch-all admin URLs.
        return custom + super().get_urls()

    def index(self, request, extra_context=None):
        """Render the dashboard if enabled, else the stock app index."""
        if not ba_conf("show_dashboard", True):
            return super().index(request, extra_context=extra_context)

        from .dashboard.registry import get_dashboard

        dashboard = get_dashboard()
        context = {
            **self.each_context(request),
            "title": self.index_title,
            "dashboard": dashboard,
            "widgets": dashboard.render(request),
            **(extra_context or {}),
        }
        request.current_app = self.name
        from django.template.response import TemplateResponse

        return TemplateResponse(request, "admin/index.html", context)


# A shared site instance. Host projects can either use this directly or build
# their own. ``sites.py`` exposes its URLConf as ``urls``.
site = BanglaAdminSite(name="bangla_admin")
