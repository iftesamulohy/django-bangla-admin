"""Chart-data providers for the default dashboard.

The default dashboard ships generic, dependency-free metrics so charts look
alive out of the box. Where real data is cheap to compute (user signups,
recent admin actions) we use it; otherwise we synthesize plausible demo series.

Host projects register their own metrics via :func:`register_metric` and point
``ChartWidget(data_url=..., params={"metric": "..."})`` at them.
"""

import datetime
import math

from django.utils import timezone

_PROVIDERS = {}


def register_metric(name):
    """Decorator to register a ``callable(request) -> {labels, datasets}``."""
    def wrap(fn):
        _PROVIDERS[name] = fn
        return fn
    return wrap


def get_chart_data(metric, request):
    provider = _PROVIDERS.get(metric, _PROVIDERS["sales"])
    return provider(request)


def _last_n_days(n):
    today = timezone.localdate()
    return [today - datetime.timedelta(days=i) for i in range(n - 1, -1, -1)]


@register_metric("sales")
def _sales(request):
    days = _last_n_days(30)
    labels = [d.strftime("%d/%m") for d in days]
    # Smooth pseudo-random-but-stable wave so it looks like a real trend.
    data = [round(120 + 60 * math.sin(i / 3.2) + (i % 5) * 8) for i in range(len(days))]
    return {
        "labels": labels,
        "datasets": [{"label": "Sales", "data": data}],
    }


@register_metric("signups")
def _signups(request):
    """Real metric: user signups per day over the last 14 days."""
    from django.contrib.auth import get_user_model

    User = get_user_model()
    days = _last_n_days(14)
    counts = []
    join_field = "date_joined"
    has_field = any(f.name == join_field for f in User._meta.get_fields())
    for d in days:
        if has_field:
            counts.append(User.objects.filter(**{f"{join_field}__date": d}).count())
        else:
            counts.append(0)
    return {
        "labels": [d.strftime("%d/%m") for d in days],
        "datasets": [{"label": "Signups", "data": counts}],
    }


@register_metric("categories")
def _categories(request):
    return {
        "labels": ["Electronics", "Fashion", "Grocery", "Books", "Other"],
        "datasets": [{"label": "Share", "data": [38, 24, 18, 12, 8]}],
    }


@register_metric("revenue")
def _revenue(request):
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    data = [round(40 + 35 * abs(math.sin(i / 1.7)) + (i % 3) * 6) for i in range(12)]
    return {
        "labels": months,
        "datasets": [{"label": "Revenue", "data": data}],
    }
