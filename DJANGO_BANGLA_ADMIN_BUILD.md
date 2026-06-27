# django-bangla-admin — Bangladeshi Django Admin Theme & Dashboard

> A free, open-source, reusable Django admin theme package (Jazzmin-style) built for a
> Bangladeshi audience. SPA-feel via HTMX, live Chart.js dashboards, Bangla ⇄ English
> language switching, and a config-driven design system.

| | |
|---|---|
| **Status** | Spec locked · **Design locked** → ready for Phase 0 |
| **Author** | Ifte Samul Ohy — iftesamulohy.com |
| **PyPI name** | `django-bangla-admin` |
| **Import name** | `django_bangla_admin` |
| **Config dict** | `BANGLA_ADMIN` |
| **License** | MIT — free & open source, published on PyPI |
| **Django support** | 4.2 LTS → 5.x (test matrix: 4.2, 5.0, 5.1, 5.2) |
| **Design reference** | `bangla-admin-preview.html` (approved) |

---

## 1. Goals & Non-Goals

### Goals
- Drop-in replacement for the default Django admin UI — install, add to `INSTALLED_APPS`, done.
- A **single config dict** (`BANGLA_ADMIN`) controls branding, menu, colors, widgets — no template editing for basic use.
- **SPA vibe without a JS framework**: HTMX-driven partial navigation, no full page reloads.
- **First-class Bangla**: full Bangla/English UI, instant language toggle, Bengali-script font stack, Bangla numerals.
- **Dashboard mood**: stat cards, live charts, recent-activity feeds — looks like a real product dashboard, not stock admin.
- **Community-friendly**: zero-build install (prebuilt CSS), no external CDN, works on BDIX/offline VPS.

### Non-Goals (v1)
- No replacement of Django's admin ORM/permissions logic — we theme and extend, not rebuild.
- No standalone frontend SPA (React/Vue). HTMX + Alpine.js only.
- No paid/license gating — fully free.

---

## 2. Tech Stack

| Layer | Choice | Reason |
|---|---|---|
| Framework | Django 4.2 LTS → 5.x | Wider reach (LTS support) |
| Interactivity | HTMX 2.x | Partial swaps, SPA feel |
| Micro-state | Alpine.js 3.x | Dropdowns, toggles, theme state |
| Styling | Tailwind CSS (compiled → shipped as static CSS) | Zero build for end users |
| Charts | Chart.js 4.x (vendored, no build step) | Lightweight, JSON-fed |
| Icons | Lucide (SVG) + Font Awesome fallback | Clean, brand-friendly |
| Fonts | Hind Siliguri / Noto Sans Bengali (Bn) + Inter (En) | Matches prior PDF/ebook work |
| i18n | Django `gettext` + cookie-based language (LocaleMiddleware) | Correct for Django 4.2+ |

> All JS/CSS/fonts are **self-hosted** inside the package — no Google Fonts or CDN dependency in production.
> (The standalone preview uses CDN fonts/Chart.js purely for convenience; the package vendors them.)

---

## 3. Brand & Design System *(locked — see preview)*

### 3.1 Color Tokens
```
/* DARK (default brand) */
--ba-bg:#0D1117; --ba-surface:#161B22; --ba-surface-2:#1C232C; --ba-surface-3:#21262D;
--ba-border:#2A323C; --ba-border-soft:#222A33;
--ba-primary:#2DD4BF; --ba-primary-700:#14B8A6; --ba-primary-tint:rgba(45,212,191,.12);
--ba-text:#E6EDF3; --ba-muted:#8B949E; --ba-faint:#6E7681;
--ba-success:#3FB950; --ba-warning:#D29922; --ba-danger:#F85149; --ba-info:#58A6FF;

/* LIGHT (token overrides only) */
--ba-bg:#F4F6F8; --ba-surface:#FFFFFF; --ba-surface-2:#FBFCFD; --ba-surface-3:#F0F3F6;
--ba-border:#E2E8EF; --ba-primary:#0E9F8E; --ba-primary-700:#0B8174;
--ba-text:#0D1117; --ba-muted:#5B6672; --ba-faint:#8893A0;
```
- **Default theme: dark.** Light variant = token overrides only.
- Theme stored in cookie + localStorage; toggled via Alpine, no reload. Charts recolor on toggle.
- Teal accent used with restraint: active nav state + accents only, never as fill-everywhere.

### 3.2 Typography
- **Bangla:** `Hind Siliguri`, fallback `Noto Sans Bengali`.
- **English / numerals:** `Inter`, fallback system stack.
- `:root[lang="bn"]` switches the active font stack; numbers use a `.num` tabular treatment.
- Fonts self-hosted in `django_bangla_admin/static/django_bangla_admin/fonts/`.

### 3.3 Layout (approved)
- Fixed left **sidebar** with grouped sections (প্রধান / সিস্টেম), icons, badges, teal active bar — **collapsible** to icon-rail.
- Sticky **topbar**: search (⌘K), language segmented toggle, theme toggle, notifications, content swaps below.
- Mobile: sidebar → off-canvas drawer.
- Content region is the **HTMX swap target** (`#ba-content`).
- Dashboard layout: 4 stat cards → line + doughnut → bar + activity feed.

---

## 4. Package Structure

```
django-bangla-admin/
├── pyproject.toml
├── README.md
├── LICENSE                       # MIT
├── MANIFEST.in
├── example/                      # demo project for testing + screenshots
└── django_bangla_admin/
    ├── __init__.py
    ├── apps.py                   # AppConfig
    ├── settings.py               # DEFAULTS + BANGLA_ADMIN merge logic
    ├── conf.py                   # `ba_conf` accessor (lazy, cached)
    ├── admin.py                  # BanglaAdminSite (extends AdminSite)
    ├── sites.py                  # site registration helpers
    ├── middleware.py             # HX-Request shell stripping
    ├── mixins.py                 # HtmxAdminMixin
    ├── context_processors.py     # injects config, lang, theme into templates
    ├── menu.py                   # menu builder (auto from models + manual)
    ├── i18n.py                   # cookie-based language switch view
    ├── dashboard/
    │   ├── __init__.py
    │   ├── base.py               # Dashboard, StatCard, ChartWidget, ListWidget
    │   ├── default.py            # DefaultDashboard
    │   ├── registry.py           # widget registration
    │   └── data.py               # JSON endpoints for charts
    ├── templatetags/
    │   ├── ba_tags.py            # {% ba_menu %}, {% ba_icon %}, {% ba_label %}
    │   └── ba_i18n.py            # {{ value|bn_number }}, dict-label resolver
    ├── views.py                  # dashboard, partials, chart-data endpoints
    ├── urls.py
    ├── locale/
    │   ├── bn/LC_MESSAGES/django.po
    │   └── en/LC_MESSAGES/django.po
    ├── static/django_bangla_admin/
    │   ├── css/bangla-admin.css   # compiled Tailwind + custom layer
    │   ├── js/bangla-admin.js     # HTMX config, Alpine inits, theme/lang toggles
    │   ├── js/charts.js           # Chart.js helpers + theme-aware palettes
    │   ├── vendor/                # htmx.min.js, alpine.min.js, chart.umd.js
    │   ├── fonts/                 # Hind Siliguri, Noto Sans Bengali, Inter
    │   └── img/
    └── templates/
        ├── admin/
        │   ├── base.html             # full shell (only on hard load)
        │   ├── base_site.html
        │   ├── index.html            # dashboard
        │   ├── change_list.html
        │   ├── change_form.html
        │   ├── login.html
        │   └── ...                   # overridden as needed
        └── django_bangla_admin/
            ├── partials/
            │   ├── _sidebar.html
            │   ├── _topbar.html
            │   ├── _content.html         # HTMX swap shell
            │   ├── _breadcrumbs.html
            │   ├── _stat_cards.html
            │   ├── _chart.html
            │   └── _activity_feed.html
            └── dashboard.html
```

---

## 5. Configuration System

A single dict in the host project's `settings.py`, merged over `DEFAULTS`.

```python
BANGLA_ADMIN = {
    # --- Branding ---
    "site_title": "Bangla Admin",
    "site_header": "Bangla Admin",
    "site_logo": "django_bangla_admin/img/logo.svg",
    "site_logo_collapsed": "django_bangla_admin/img/mark.svg",
    "welcome_sign": "স্বাগতম, Admin Panel-এ",
    "copyright": "iftesamulohy.com",

    # --- Theme ---
    "theme": "dark",                # "dark" | "light"
    "allow_theme_toggle": True,
    "primary_color": "#2DD4BF",

    # --- Language ---
    "default_language": "bn",       # "bn" | "en"
    "allow_language_toggle": True,
    "languages": ["bn", "en"],
    "bangla_numerals": True,        # render ০১২৩ when lang == bn

    # --- Navigation (sidebar) ---
    "show_sidebar": True,
    "sidebar_collapsible": True,
    "navigation_expanded": True,
    "menu": [                       # optional; auto-built from models if omitted
        {"section": {"bn": "প্রধান", "en": "Main"}},
        {"label": {"bn": "ড্যাশবোর্ড", "en": "Dashboard"},
         "icon": "layout-dashboard", "url": "bangla_admin:dashboard"},
        {"label": {"bn": "ব্যবহারকারী", "en": "Users"},
         "icon": "users", "model": "auth.User"},
        {"label": {"bn": "অর্ডার", "en": "Orders"},
         "icon": "shopping-cart", "model": "shop.Order"},
        {"section": {"bn": "সিস্টেম", "en": "System"}},
        {"label": {"bn": "সেটিংস", "en": "Settings"}, "icon": "settings", "url": "..."},
    ],
    "icons": {"auth.User": "user", "auth.Group": "users"},   # per-model icons
    "hide_apps": [],
    "hide_models": [],

    # --- Dashboard ---
    "dashboard": "django_bangla_admin.dashboard.default.DefaultDashboard",
    "show_dashboard": True,

    # --- HTMX ---
    "spa_navigation": True,
    "swap_target": "#ba-content",
}
```

Accessor: `from django_bangla_admin.conf import ba_conf` → `ba_conf("theme")` — lazy, cached, deep-merged over defaults.

---

## 6. HTMX SPA Navigation

On a **hard load** the full shell renders (`base.html`: sidebar + topbar + content). After that, internal navigation only swaps the content region.

### 6.1 Mechanism
1. `base.html` wraps the main region in `<main id="ba-content">`.
2. In-app links auto-decorated (`hx-get`, `hx-target="#ba-content"`, `hx-swap="innerHTML"`, `hx-push-url="true"`) via `bangla-admin.js` — model admins need no manual attributes.
3. Server detects HTMX requests via the `HX-Request` header (`middleware.py`) and returns only the **content partial**, not the full shell.
4. History via `hx-push-url`; back/forward re-fetch partials.

### 6.2 Partial-aware response
```python
# django_bangla_admin/mixins.py
class HtmxAdminMixin:
    def get_template_names(self):
        base = super().get_template_names()
        if self.request.headers.get("HX-Request"):
            return ["django_bangla_admin/partials/_content.html", *base]
        return base
```
For Django admin's own change_list/change_form, the middleware strips the outer shell when `HX-Request` is present (using the `{% block ba_content %}` boundary).

### 6.3 UX niceties
- Teal 2px **progress bar** via HTMX `hx-indicator`.
- Active sidebar item updates on `htmx:afterSwap` (reads `HX-Current-URL`).
- change_form submits use `hx-boost` so saves don't full-reload.
- messages-framework toasts injected via out-of-band swap into `#ba-toasts`.
- **Charts re-init on `htmx:afterSwap`** so they survive SPA navigation.

---

## 7. Dashboard & Charts (Chart.js)

### 7.1 Layout
```
┌───────────────────────────────────────────────┐
│  4 × Stat Cards (KPIs, delta badge)             │
├───────────────────────┬───────────────────────┤
│  Line/Area (sales 30d)│  Doughnut (categories) │
├───────────────────────┴───────────────────────┤
│  Bar (monthly revenue) │  Recent Activity Feed │
└───────────────────────────────────────────────┘
```

### 7.2 Widget system
```python
# django_bangla_admin/dashboard/default.py
from django_bangla_admin.dashboard import Dashboard, StatCard, ChartWidget, ListWidget

class DefaultDashboard(Dashboard):
    widgets = [
        StatCard(label={"bn": "মোট ব্যবহারকারী", "en": "Total Users"},
                 value=lambda r: User.objects.count(), icon="users", trend="+12%"),
        StatCard(label={"bn": "আজকের অর্ডার", "en": "Orders Today"}, value=..., icon="shopping-cart"),
        ChartWidget(id="sales", kind="line",
                    title={"bn": "বিক্রির প্রবণতা", "en": "Sales Trend"},
                    data_url="bangla_admin:chart-data", params={"metric": "sales"}),
        ChartWidget(id="cats", kind="doughnut",
                    title={"bn": "ক্যাটাগরি ভাগ", "en": "Category Split"}, ...),
        ListWidget(id="activity", title={"bn": "সাম্প্রতিক কার্যক্রম", "en": "Recent Activity"},
                   source=lambda r: LogEntry.objects.all()[:10]),
    ]
```

### 7.3 Chart data flow
- Charts fetch JSON from `GET /admin/ba/chart-data/?metric=sales` (staff-only).
- `charts.js` builds Chart.js configs with **theme-aware palettes** (reads CSS vars → recolors on theme/lang toggle).
- Axis numbers rendered in **Bangla numerals** when `lang == bn`.
- Host projects register custom `data_url` endpoints returning `{labels: [...], datasets: [...]}`.

---

## 8. Internationalization (Bangla ⇄ English)

### 8.1 Strategy
- All package UI strings wrapped in `gettext` / `{% trans %}` → `locale/bn` + `locale/en`.
- Menu/model labels accept a string **or** a `{"bn": ..., "en": ...}` dict, resolved by `{% ba_label %}` / `ba_i18n`.
- Language handled the **Django 4.2-correct way**: cookie (`LANGUAGE_COOKIE_NAME`) + `LocaleMiddleware`. *(Session-based language was removed in Django 4.0 — do not use `LANGUAGE_SESSION_KEY`.)*

### 8.2 Required host settings
```python
USE_I18N = True
LANGUAGE_CODE = "bn"
LANGUAGES = [("bn", "বাংলা"), ("en", "English")]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",      # after Session, before Common
    "django.middleware.common.CommonMiddleware",
    # ...
]
```

### 8.3 Switch endpoint
```python
# django_bangla_admin/i18n.py
from django.utils import translation
from django.conf import settings
from django.http import HttpResponse

def set_language(request):
    lang = request.GET.get("lang", "bn")
    if lang not in dict(settings.LANGUAGES):
        lang = settings.LANGUAGE_CODE
    translation.activate(lang)
    resp = render_chrome(request)            # HTMX: re-render sidebar/topbar/content OOB
    resp.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang,
                    max_age=365 * 24 * 3600, samesite="Lax")
    resp["HX-Trigger"] = "lang-changed"      # client flips <html lang> + font stack
    return resp
```
- Topbar segmented toggle (`বাং / EN`) fires `hx-get` → swaps chrome + content **without full reload**.
- `<html lang="...">` updated client-side so the correct font stack applies instantly.

### 8.4 Bangla numerals
- `{{ value|bn_number }}` → `1234` becomes `১২৩৪` when active language is Bangla (gated by `bangla_numerals`).

---

## 9. Installation (target end-user experience)

```bash
pip install django-bangla-admin
```
```python
# settings.py
INSTALLED_APPS = [
    "django_bangla_admin",      # BEFORE django.contrib.admin
    "django.contrib.admin",
    ...
]
BANGLA_ADMIN = {"site_title": "My Shop Admin", "default_language": "bn"}
```
```python
# urls.py
from django_bangla_admin.sites import urls as ba_urls
urlpatterns = [path("admin/", ba_urls)]
```
No template edits required for a fully themed, Bangla, HTMX-driven admin with charts.

---

## 10. Implementation Phases

> Each phase ends with a runnable demo project (`/example`).

### Phase 0 — Scaffolding
`pyproject.toml`, package skeleton, `AppConfig`, `/example` project, Tailwind build pipeline → compiled CSS, vendored JS/fonts.
**Done when:** `pip install -e .` works, themed `base.html` renders.

### Phase 1 — Theme Shell & Static
Color tokens, fonts (Bn + En), `base.html` shell (sidebar + topbar + content), dark theme, login override. Match the approved preview.
**Done when:** default admin is fully reskinned (no HTMX yet).

### Phase 2 — Config System
`BANGLA_ADMIN` defaults + deep-merge, `ba_conf`, context processor, branding wired.
**Done when:** changing the dict changes the UI with zero template edits.

### Phase 3 — Sidebar Menu & Navigation
Auto menu from registered models + manual menu/sections, icon mapping, badges, active state, collapsible sidebar, mobile drawer.

### Phase 4 — HTMX SPA Layer
Swap target, link decoration, `HX-Request` partials, history, progress bar, boosted forms, toasts.
**Done when:** navigating the admin never full-reloads.

### Phase 5 — i18n / Language Switch
`locale/bn` + `locale/en`, dict-label resolution, cookie language + LocaleMiddleware, topbar toggle, font swap, Bangla numerals.

### Phase 6 — Dashboard & Charts
Dashboard registry, StatCard/ChartWidget/ListWidget, chart-data JSON endpoints, theme-aware Chart.js, activity feed.
**Done when:** dashboard shows live KPIs + 3 charts, recolors on theme/lang toggle.

### Phase 7 — Theme Toggle & Light Mode
Light token set, persisted toggle, charts/components respect it.

### Phase 8 — Polish, Docs & PyPI Publish
Theme-aware change_form/change_list, empty states, a11y (focus rings, reduced-motion), README with screenshots/GIF, `pyproject` metadata + classifiers + `MANIFEST.in`, `python -m build`, `twine upload`, public GitHub repo (MIT, CI for tests + lint across the Django matrix).

---

## 11. Acceptance Checklist (v1)

- [ ] Install + 3 lines of config → fully themed admin, zero template edits.
- [ ] Dark theme default; light toggle persists across navigation.
- [ ] Bangla default; instant Bn ⇄ En toggle (chrome + content + font + numerals).
- [ ] Sidebar auto-builds from models; manual menu, sections, icons, badges honored; collapsible + mobile drawer.
- [ ] SPA navigation: no full reloads; back/forward works; progress bar shows.
- [ ] Dashboard: 4 stat cards + line + doughnut + bar charts + activity feed.
- [ ] Charts pull live JSON and recolor on theme/lang change; survive SPA swaps.
- [ ] Self-hosted fonts + vendored JS (no external CDN) — works on BDIX/offline VPS.
- [ ] Works on Django 4.2, 5.0, 5.1, 5.2.
- [ ] Demo `/example` boots with `python manage.py runserver` (seeded data).
- [ ] Published to PyPI as `django-bangla-admin`, MIT, public GitHub repo.

---

## 12. Resolved Decisions

1. **Django support** → 4.2 LTS → 5.x. ✅
2. **Charts** → Chart.js (light, vendored). ✅
3. **Import name** → `django_bangla_admin`; config dict `BANGLA_ADMIN`. ✅
4. **License/distribution** → MIT, free, PyPI + public GitHub. ✅
5. **Design** → locked to `bangla-admin-preview.html` (dark default, teal accent, Hind Siliguri + Inter). ✅
6. **Sidebar** → yes, grouped menu with auto + manual modes. ✅
7. **GitHub repo name** → `django-bangla-admin` (matches PyPI). ✅
8. **Demo data** → ship a seed script in `/example` (users + orders + categories) so charts look alive. ✅
