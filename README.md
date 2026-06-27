# django-bangla-admin

> A free, open-source, reusable **Django admin theme & dashboard** built for a
> Bangladeshi audience. SPA-feel via HTMX, live Chart.js dashboards,
> **Bangla ⇄ English** language switching, and a single config dict — no
> template editing for basic use.

[![License: MIT](https://img.shields.io/badge/License-MIT-14B8A6.svg)](LICENSE)
[![Django](https://img.shields.io/badge/Django-4.2%20→%205.x-0C4B33.svg)](https://www.djangoproject.com/)

![Dashboard — dark, Bangla](docs/screenshots/dashboard-dark-bn.png)

<p align="center">
  <img src="docs/screenshots/dashboard-light-en.png" width="49%" alt="Dashboard — light, English">
  <img src="docs/screenshots/changelist-dark-bn.png" width="49%" alt="Changelist — dark, Bangla">
</p>

---

## Features

- 🎨 **Drop-in theme** — install, add to `INSTALLED_APPS`, point your URLs at it. No template edits required.
- ⚙️ **One config dict** (`BANGLA_ADMIN`) controls branding, menu, colors, dashboard.
- ⚡ **SPA feel, no JS framework** — HTMX partial navigation; the admin never full-reloads.
- 🇧🇩 **First-class Bangla** — full Bn/En UI, instant cookie-based toggle, Bengali font stack, Bangla numerals (০১২৩).
- 📊 **Live dashboard** — stat cards, line / doughnut / bar charts (Chart.js), activity feed; charts recolor on theme/lang change.
- 🧩 **Charts & KPIs from settings** — declare *which model, which field/status, which aggregation, which chart type* in `BANGLA_ADMIN`; the ORM query runs for you. No Python needed. ([docs](#charts--kpis-from-settings-no-python))
- 🌗 **Dark default + light mode** — persisted toggle; charts and components follow.
- 📦 **Zero-build, offline-friendly** — prebuilt CSS, self-hosted fonts, vendored HTMX / Alpine / Chart.js. No CDN. Works on BDIX / offline VPS.

## Installation

```bash
pip install django-bangla-admin
```

```python
# settings.py
INSTALLED_APPS = [
    "django_bangla_admin",      # BEFORE django.contrib.admin
    "django.contrib.admin",
    # ...
]

# i18n (the Django 4.2+ correct way — cookie + LocaleMiddleware)
USE_I18N = True
LANGUAGE_CODE = "bn"
LANGUAGES = [("bn", "বাংলা"), ("en", "English")]

MIDDLEWARE = [
    # ...
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",          # after Session, before Common
    "django.middleware.common.CommonMiddleware",
    # ...
    "django_bangla_admin.middleware.HtmxShellMiddleware",  # strips shell on HX-Request
]

# Add the context processor for theme/language in templates
TEMPLATES[0]["OPTIONS"]["context_processors"] += [
    "django_bangla_admin.context_processors.bangla_admin",
]

BANGLA_ADMIN = {"site_title": "My Shop Admin", "default_language": "bn"}
```

```python
# urls.py
from django.urls import path
from django_bangla_admin.sites import urls as ba_urls

urlpatterns = [path("admin/", ba_urls)]
```

That's it — a fully themed, Bangla, HTMX-driven admin with charts. Your existing
`@admin.register` / `admin.site.register` calls work unchanged: the themed site
mirrors the default admin registry automatically.

## Configuration

A single `BANGLA_ADMIN` dict, deep-merged over the defaults:

```python
BANGLA_ADMIN = {
    # Branding
    "site_title": "Bangla Admin",
    "site_brand": {"bn": "বাংলা অ্যাডমিন", "en": "Bangla Admin"},
    "welcome_sign": {"bn": "স্বাগতম", "en": "Welcome"},

    # Theme
    "theme": "dark",                 # "dark" | "light"
    "allow_theme_toggle": True,
    "primary_color": "#2DD4BF",

    # Language
    "default_language": "bn",
    "allow_language_toggle": True,
    "bangla_numerals": True,

    # Navigation — omit `menu` to auto-build from registered models
    "menu": [
        {"section": {"bn": "প্রধান", "en": "Main"}},
        {"label": {"bn": "ড্যাশবোর্ড", "en": "Dashboard"},
         "icon": "layout-dashboard", "url": "bangla_admin:index"},
        {"label": {"bn": "অর্ডার", "en": "Orders"},
         "icon": "shopping-cart", "model": "shop.Order"},
    ],
    "icons": {"auth.User": "user"},  # per-model Lucide icons
    "hide_apps": [], "hide_models": [],

    # Dashboard
    "dashboard": "django_bangla_admin.dashboard.default.DefaultDashboard",
    "show_dashboard": True,
}
```

Read values anywhere via `from django_bangla_admin.conf import ba_conf` → `ba_conf("theme")`.

## Charts & KPIs from settings (no Python)

You can build the whole dashboard **declaratively from `BANGLA_ADMIN`** — say
which model, which field/status, how to aggregate, and which chart type. The
package runs the ORM query for you. When you declare `charts` and/or
`stat_cards`, they replace the built-in demo widgets.

```python
BANGLA_ADMIN = {
    # KPI cards across the top
    "stat_cards": [
        {"label": {"bn": "মোট অর্ডার", "en": "Total Orders"},
         "model": "shop.Order", "aggregate": "count", "icon": "shopping-cart", "trend": "+9%"},

        {"label": {"bn": "পরিশোধিত আয়", "en": "Paid Revenue"},
         "model": "shop.Order", "aggregate": "sum", "field": "total",
         "filters": {"status": "paid"}, "icon": "trending-up"},
    ],

    # Charts
    "charts": [
        # Doughnut: count orders grouped by their status (choice labels resolved)
        {"id": "orders_by_status", "kind": "doughnut",
         "title": {"bn": "অর্ডার স্ট্যাটাস", "en": "Orders by Status"},
         "model": "shop.Order", "group_by": "status", "aggregate": "count"},

        # Bar: monthly paid revenue (date field truncated to month, sum of `total`)
        {"id": "revenue_by_month", "kind": "bar",
         "title": {"bn": "মাসিক আয়", "en": "Monthly Revenue"},
         "model": "shop.Order", "group_by": "created_at", "trunc": "month",
         "aggregate": "sum", "field": "total",
         "filters": {"status": "paid"}, "limit": 12},

        # Bar: products per category (follows the FK with `__`)
        {"id": "products_per_category", "kind": "bar",
         "title": {"bn": "ক্যাটাগরি অনুযায়ী পণ্য", "en": "Products per Category"},
         "model": "shop.Product", "group_by": "category__name", "aggregate": "count"},
    ],
}
```

### Chart options

| Key | Required | Description |
|---|---|---|
| `id` | ✅ | Unique id (used as the canvas id and `?chart=` key). |
| `kind` | ✅ | `line` · `bar` · `doughnut` · `pie`. |
| `title` | ✅ | String or `{"bn": ..., "en": ...}` dict. |
| `model` | ✅ | `"app_label.ModelName"`. |
| `group_by` | ✅ | Field to group by. Use `__` to follow relations (`category__name`). For a **date/datetime** field, add `trunc`. |
| `aggregate` | ✅ | `count` · `sum` · `avg` · `min` · `max`. |
| `field` |  | Field to aggregate. Required for everything except `count`. |
| `trunc` |  | For date `group_by`: `day` · `week` · `month` · `year` (time-series buckets, ordered chronologically). |
| `filters` |  | Dict of ORM filters applied first, e.g. `{"status": "paid", "is_active": True}`. Keys support lookups (`created_at__year`). |
| `limit` |  | Keep the top *N* groups (or last *N* time buckets). |
| `size` |  | Grid width class: `ba-col-12` · `ba-col-6` (default) · `ba-col-4` · `ba-col-3`. |

### Stat-card options

| Key | Required | Description |
|---|---|---|
| `label` | ✅ | String or `{"bn", "en"}` dict. |
| `model` | ✅ | `"app_label.ModelName"`. |
| `aggregate` | ✅ | `count` · `sum` · `avg` · `min` · `max`. |
| `field` |  | Required for everything except `count`. |
| `filters` |  | Dict of ORM filters. |
| `icon` |  | Lucide icon name (e.g. `shopping-cart`, `users`, `package`). |
| `trend` / `trend_dir` |  | Badge text (e.g. `"+9%"`) and direction (`up`/`down`). |

> Group values are humanized automatically — fields with `choices` show their
> display label, and Bangla numerals are applied to chart axes and KPI values
> when the active language is Bangla. Decimal sums are returned as numbers.

## Advanced: custom dashboards & metrics (Python)

For anything the declarative API can't express, drop to Python. Subclass
`Dashboard` and point `BANGLA_ADMIN["dashboard"]` at it:

```python
from django_bangla_admin.dashboard import Dashboard, StatCard, ChartWidget, ListWidget

class MyDashboard(Dashboard):
    widgets = [
        StatCard(label={"bn": "অর্ডার", "en": "Orders"},
                 value=lambda r: Order.objects.count(), icon="shopping-cart", trend="+8%"),
        ChartWidget(id="sales", kind="line",
                    title={"bn": "বিক্রি", "en": "Sales"},
                    data_url="bangla_admin:ba_chart_data", params={"metric": "sales"}),
    ]
```

Register fully custom chart metrics with `@register_metric("name")` from
`django_bangla_admin.dashboard.data`, returning `{"labels": [...], "datasets": [...]}`:

```python
from django_bangla_admin.dashboard.data import register_metric

@register_metric("sales")
def my_sales(request):
    return {"labels": [...], "datasets": [{"label": "Sales", "data": [...]}]}
```

Then reference it from a `ChartWidget(data_url="bangla_admin:ba_chart_data", params={"metric": "sales"})`.

## Demo project

```bash
cd example
python manage.py migrate
python manage.py seed_demo      # creates admin/admin + sample shop data
python manage.py runserver
```

Open <http://127.0.0.1:8000/admin/> and log in with **admin / admin**.

## Development

```bash
pip install -e .
python -m django test tests --settings=tests.settings   # run the suite
python scripts/compile_messages.py                       # compile .po -> .mo (no gettext needed)
```

## Tech

HTMX 2 · Alpine.js 3 · Chart.js 4 · self-hosted Hind Siliguri / Inter fonts ·
Django 4.2 LTS → 5.x.

## License

MIT © [Ifte Samul Ohy](https://iftesamulohy.com)
