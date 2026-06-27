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

from ..conf import ba_conf

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


# ---------------------------------------------------------------------------
# Declarative, settings-driven charts (no Python required by the end user).
#
# A chart is described in ``BANGLA_ADMIN["charts"]`` and resolved against the
# ORM here. Example::
#
#     {"id": "orders_by_status", "kind": "doughnut",
#      "title": {"bn": "অর্ডার স্ট্যাটাস", "en": "Orders by Status"},
#      "model": "shop.Order", "group_by": "status", "aggregate": "count"}
# ---------------------------------------------------------------------------

_DATE_FORMATS = {"day": "%d/%m", "week": "%d/%m", "month": "%b %Y", "year": "%Y"}


def _find_config(key, item_id):
    for item in (ba_conf(key, []) or []):
        if item.get("id") == item_id:
            return item
    return None


def _build_aggregate(aggregate, field):
    """Return a Django aggregate expression for ``aggregate`` over ``field``."""
    from django.db.models import Avg, Count, Max, Min, Sum

    funcs = {"count": Count, "sum": Sum, "avg": Avg, "min": Min, "max": Max}
    if aggregate not in funcs:
        raise ValueError(
            f"Unknown aggregate {aggregate!r}; use one of {sorted(funcs)}."
        )
    if aggregate == "count":
        return Count(field or "id")
    if not field:
        raise ValueError(f"aggregate {aggregate!r} requires a 'field'.")
    return funcs[aggregate](field)


def _trunc(trunc, group_by):
    from django.db.models.functions import (
        TruncDay, TruncMonth, TruncWeek, TruncYear,
    )

    funcs = {"day": TruncDay, "week": TruncWeek, "month": TruncMonth, "year": TruncYear}
    if trunc not in funcs:
        raise ValueError(f"Unknown trunc {trunc!r}; use one of {sorted(funcs)}.")
    return funcs[trunc](group_by)


def _display_label(model, group_by, value):
    """Resolve a grouped value to a human label (maps field choices)."""
    if value is None:
        return "—"
    if "__" not in group_by:
        try:
            field = model._meta.get_field(group_by)
            choices = getattr(field, "flatchoices", None)
            if choices:
                return str(dict(choices).get(value, value))
        except Exception:
            pass
    return str(value)


def resolve_config_chart(chart_id, request):
    """Build ``{labels, datasets}`` for a chart declared in settings."""
    from django.apps import apps

    cfg = _find_config("charts", chart_id)
    if not cfg:
        return {"labels": [], "datasets": []}

    from ..templatetags.ba_i18n import resolve_label

    model = apps.get_model(cfg["model"])
    qs = model._default_manager.all()
    if cfg.get("filters"):
        qs = qs.filter(**cfg["filters"])

    agg = _build_aggregate(cfg.get("aggregate", "count"), cfg.get("field"))
    group_by = cfg["group_by"]
    limit = cfg.get("limit")

    if cfg.get("trunc"):
        rows = list(
            qs.annotate(_bucket=_trunc(cfg["trunc"], group_by))
            .values("_bucket")
            .annotate(_value=agg)
            .order_by("_bucket")
        )
        if limit:
            rows = rows[-limit:]
        fmt = _DATE_FORMATS[cfg["trunc"]]
        labels = [r["_bucket"].strftime(fmt) if r["_bucket"] else "—" for r in rows]
    else:
        rows = list(
            qs.values(group_by).annotate(_value=agg).order_by("-_value")
        )
        if limit:
            rows = rows[:limit]
        labels = [_display_label(model, group_by, r[group_by]) for r in rows]

    data = [_to_number(r["_value"]) for r in rows]
    return {
        "labels": labels,
        "datasets": [{"label": resolve_label(cfg.get("title", "")), "data": data}],
    }


def _to_number(value):
    """Coerce ORM aggregate results (Decimal/None) to JSON-plottable numbers."""
    import decimal

    if value is None:
        return 0
    if isinstance(value, decimal.Decimal):
        value = float(value)
    # Drop a meaningless trailing ".0" so KPIs read "2299635", not "2299635.0".
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return value


def resolve_stat_card(cfg, request):
    """Compute the value for a declarative stat card config."""
    from django.apps import apps

    model = apps.get_model(cfg["model"])
    qs = model._default_manager.all()
    if cfg.get("filters"):
        qs = qs.filter(**cfg["filters"])
    aggregate = cfg.get("aggregate", "count")
    if aggregate == "count":
        return qs.count()
    result = qs.aggregate(_v=_build_aggregate(aggregate, cfg.get("field")))
    return _to_number(result["_v"])
