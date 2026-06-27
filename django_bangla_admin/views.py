"""Views: chart-data JSON endpoint (staff-only via admin_view wrapping)."""

from django.http import JsonResponse

from .dashboard.data import get_chart_data


def chart_data(request):
    """Return ``{"labels": [...], "datasets": [...]}`` for a metric.

    Wrapped by ``BanglaAdminSite.admin_view`` so it is staff-only. Charts fetch
    this from ``charts.js`` and apply theme-aware palettes client-side.
    """
    metric = request.GET.get("metric", "sales")
    data = get_chart_data(metric, request)
    return JsonResponse(data)
