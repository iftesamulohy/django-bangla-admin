"""The default dashboard: stat cards + charts + activity feed.

By default it shows generic, dependency-free demo content (auth + LogEntry) so
it renders for any project. But when the host project declares ``stat_cards``
and/or ``charts`` in ``BANGLA_ADMIN``, those ORM-driven widgets are used
instead — no Python required. See docs "Charts from settings".
"""

from ..conf import ba_conf
from .base import ChartWidget, Dashboard, ListWidget, StatCard


def _user_count(request):
    from django.contrib.auth import get_user_model
    return get_user_model().objects.count()


def _staff_count(request):
    from django.contrib.auth import get_user_model
    return get_user_model().objects.filter(is_staff=True).count()


def _today_signups(request):
    from django.contrib.auth import get_user_model
    from django.utils import timezone
    User = get_user_model()
    if not any(f.name == "date_joined" for f in User._meta.get_fields()):
        return 0
    return User.objects.filter(date_joined__date=timezone.localdate()).count()


def _action_count(request):
    from django.contrib.admin.models import LogEntry
    return LogEntry.objects.count()


def _recent_actions(request):
    from django.contrib.admin.models import LogEntry
    return list(LogEntry.objects.select_related("user", "content_type")[:8])


def build_config_stat_cards():
    """StatCards declared in ``BANGLA_ADMIN["stat_cards"]`` (ORM-driven)."""
    from .data import resolve_stat_card

    cards = []
    for cfg in (ba_conf("stat_cards", []) or []):
        cards.append(StatCard(
            label=cfg.get("label", cfg.get("model", "")),
            value=(lambda c: (lambda request: resolve_stat_card(c, request)))(cfg),
            icon=cfg.get("icon", "circle-dot"),
            trend=cfg.get("trend"),
            trend_dir=cfg.get("trend_dir", "up"),
        ))
    return cards


def build_config_charts():
    """ChartWidgets declared in ``BANGLA_ADMIN["charts"]`` (ORM-driven)."""
    charts = []
    for cfg in (ba_conf("charts", []) or []):
        charts.append(ChartWidget(
            id=cfg["id"],
            kind=cfg.get("kind", "bar"),
            title=cfg.get("title", cfg["id"]),
            data_url="bangla_admin:ba_chart_data",
            params={"chart": cfg["id"]},
            size=cfg.get("size"),
        ))
    return charts


# Built-in demo widgets, used when the host project declares no config widgets.
_DEMO_STAT_CARDS = [
    StatCard(label={"bn": "মোট ব্যবহারকারী", "en": "Total Users"},
             value=_user_count, icon="users", trend="+12%"),
    StatCard(label={"bn": "স্টাফ", "en": "Staff"},
             value=_staff_count, icon="shield", trend="+3%"),
    StatCard(label={"bn": "আজকের সাইনআপ", "en": "Signups Today"},
             value=_today_signups, icon="user", trend="+5%"),
    StatCard(label={"bn": "মোট অ্যাকশন", "en": "Total Actions"},
             value=_action_count, icon="activity", trend="+18%"),
]
_DEMO_CHARTS = [
    ChartWidget(id="sales", kind="line",
                title={"bn": "বিক্রির প্রবণতা (৩০ দিন)", "en": "Sales Trend (30d)"},
                data_url="bangla_admin:ba_chart_data", params={"metric": "sales"}),
    ChartWidget(id="cats", kind="doughnut",
                title={"bn": "ক্যাটাগরি ভাগ", "en": "Category Split"},
                data_url="bangla_admin:ba_chart_data", params={"metric": "categories"}),
    ChartWidget(id="revenue", kind="bar",
                title={"bn": "মাসিক আয়", "en": "Monthly Revenue"},
                data_url="bangla_admin:ba_chart_data", params={"metric": "revenue"}),
]


class DefaultDashboard(Dashboard):
    def get_widgets(self, request):
        stat_cards = build_config_stat_cards() or _DEMO_STAT_CARDS
        charts = build_config_charts() or _DEMO_CHARTS
        activity = ListWidget(
            id="activity",
            title={"bn": "সাম্প্রতিক কার্যক্রম", "en": "Recent Activity"},
            source=_recent_actions,
        )
        return [*stat_cards, *charts, activity]
