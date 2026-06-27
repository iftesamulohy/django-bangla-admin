"""Dashboard and widget primitives.

A ``Dashboard`` is a declarative list of widgets. Each widget knows how to
produce a small context dict (``render(request)``) that the dashboard template
iterates over. Widgets carry a ``template`` and a ``size`` (Tailwind column
span hint) so the dashboard grid stays config-driven.
"""


def _callable_value(value, request):
    """Resolve ``value`` that may be a plain value or a ``callable(request)``."""
    if callable(value):
        try:
            return value(request)
        except TypeError:
            return value()
    return value


class Widget:
    template = "django_bangla_admin/partials/_widget.html"
    size = "ba-col-12"  # default full width (12-col grid, see bangla-admin.css)

    def __init__(self, id=None, title=None, size=None):
        self.id = id
        self.title = title
        if size:
            self.size = size

    def get_context(self, request):
        return {"id": self.id, "title": self.title}

    def render(self, request):
        return {
            "template": self.template,
            "size": self.size,
            "context": self.get_context(request),
        }


class StatCard(Widget):
    template = "django_bangla_admin/partials/_stat_card.html"
    size = "ba-col-3"

    def __init__(self, label, value, icon="circle-dot", trend=None,
                 trend_dir="up", **kwargs):
        super().__init__(**kwargs)
        self.label = label
        self.value = value
        self.icon = icon
        self.trend = trend
        self.trend_dir = trend_dir

    def get_context(self, request):
        return {
            "label": self.label,
            "value": _callable_value(self.value, request),
            "icon": self.icon,
            "trend": self.trend,
            "trend_dir": self.trend_dir,
        }


class ChartWidget(Widget):
    template = "django_bangla_admin/partials/_chart.html"
    size = "ba-col-6"

    def __init__(self, id, kind, title, data_url=None, params=None,
                 static_data=None, **kwargs):
        super().__init__(id=id, title=title, **kwargs)
        self.kind = kind            # "line" | "bar" | "doughnut" | ...
        self.data_url = data_url    # url name, resolved at render
        self.params = params or {}
        self.static_data = static_data  # optional inline {labels, datasets}

    def get_context(self, request):
        from django.urls import NoReverseMatch, reverse

        url = ""
        if self.data_url:
            try:
                base = reverse(self.data_url)
            except NoReverseMatch:
                base = self.data_url
            query = "&".join(f"{k}={v}" for k, v in self.params.items())
            url = f"{base}?{query}" if query else base
        return {
            "id": self.id,
            "title": self.title,
            "kind": self.kind,
            "data_url": url,
            "static_data": self.static_data,
        }


class ListWidget(Widget):
    template = "django_bangla_admin/partials/_activity_feed.html"
    size = "ba-col-6"

    def __init__(self, id, title, source, render_item=None, **kwargs):
        super().__init__(id=id, title=title, **kwargs)
        self.source = source
        self.render_item = render_item

    def get_context(self, request):
        items = _callable_value(self.source, request)
        return {
            "id": self.id,
            "title": self.title,
            "items": list(items) if items is not None else [],
            "render_item": self.render_item,
        }


class Dashboard:
    """Declarative dashboard. Subclass and set ``widgets``."""

    widgets = []

    def get_widgets(self, request):
        return self.widgets

    def render(self, request):
        return [w.render(request) for w in self.get_widgets(request)]
