"""Views: chart-data JSON endpoint (staff-only via admin_view wrapping)."""

from django.http import JsonResponse

from .dashboard.data import get_chart_data, resolve_config_chart


def chart_data(request):
    """Return ``{"labels": [...], "datasets": [...]}`` for a chart.

    Wrapped by ``BanglaAdminSite.admin_view`` so it is staff-only. Charts fetch
    this from ``charts.js`` and apply theme-aware palettes client-side.

    Two modes:
    * ``?chart=<id>`` — a declarative chart from ``BANGLA_ADMIN["charts"]``,
      resolved against the ORM.
    * ``?metric=<name>`` — a built-in or code-registered metric provider.
    """
    chart_id = request.GET.get("chart")
    if chart_id:
        return JsonResponse(resolve_config_chart(chart_id, request))
    metric = request.GET.get("metric", "sales")
    return JsonResponse(get_chart_data(metric, request))
