"""The default dashboard: 4 stat cards + line + doughnut + bar + activity feed.

Uses only Django's bundled models (auth + admin LogEntry) so it renders for any
project without configuration. Host projects override via
``BANGLA_ADMIN['dashboard']``.
"""

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


class DefaultDashboard(Dashboard):
    widgets = [
        StatCard(
            label={"bn": "মোট ব্যবহারকারী", "en": "Total Users"},
            value=_user_count, icon="users", trend="+12%", trend_dir="up",
        ),
        StatCard(
            label={"bn": "স্টাফ", "en": "Staff"},
            value=_staff_count, icon="shield", trend="+3%", trend_dir="up",
        ),
        StatCard(
            label={"bn": "আজকের সাইনআপ", "en": "Signups Today"},
            value=_today_signups, icon="user", trend="+5%", trend_dir="up",
        ),
        StatCard(
            label={"bn": "মোট অ্যাকশন", "en": "Total Actions"},
            value=_action_count, icon="activity", trend="+18%", trend_dir="up",
        ),
        ChartWidget(
            id="sales", kind="line",
            title={"bn": "বিক্রির প্রবণতা (৩০ দিন)", "en": "Sales Trend (30d)"},
            data_url="bangla_admin:ba_chart_data", params={"metric": "sales"},
        ),
        ChartWidget(
            id="cats", kind="doughnut",
            title={"bn": "ক্যাটাগরি ভাগ", "en": "Category Split"},
            data_url="bangla_admin:ba_chart_data", params={"metric": "categories"},
        ),
        ChartWidget(
            id="revenue", kind="bar",
            title={"bn": "মাসিক আয়", "en": "Monthly Revenue"},
            data_url="bangla_admin:ba_chart_data", params={"metric": "revenue"},
        ),
        ListWidget(
            id="activity",
            title={"bn": "সাম্প্রতিক কার্যক্রম", "en": "Recent Activity"},
            source=_recent_actions,
        ),
    ]
