"""Reusable mixins for HTMX-aware class-based admin/custom views."""


class HtmxAdminMixin:
    """Return a content-only partial template for HTMX requests.

    Mix into any ``TemplateView``-style view that should participate in SPA
    navigation. Django's own admin views go through ``HtmxShellMiddleware``
    instead (they don't use ``get_template_names`` the same way).
    """

    htmx_partial = "django_bangla_admin/partials/_content.html"

    def get_template_names(self):
        base = super().get_template_names()
        if self.request.headers.get("HX-Request") == "true":
            return [self.htmx_partial, *base]
        return base
