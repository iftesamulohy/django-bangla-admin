"""Default configuration for django-bangla-admin.

The host project overrides any of these via a ``BANGLA_ADMIN`` dict in its
Django settings. Values are deep-merged over these defaults by ``conf.ba_conf``.
"""

DEFAULTS = {
    # --- Branding ---
    "site_title": "Bangla Admin",
    "site_header": "Bangla Admin",
    "site_brand": {"bn": "বাংলা অ্যাডমিন", "en": "Bangla Admin"},
    "site_logo": None,
    "site_logo_collapsed": None,
    "welcome_sign": {"bn": "স্বাগতম, Admin Panel-এ", "en": "Welcome to the Admin Panel"},
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
    "menu": None,                   # None -> auto-built from registered models
    "icons": {                      # per-model icons (Lucide names)
        "auth.User": "user",
        "auth.Group": "users",
    },
    "default_icon": "circle-dot",
    "hide_apps": [],
    "hide_models": [],

    # --- Dashboard ---
    "dashboard": "django_bangla_admin.dashboard.default.DefaultDashboard",
    "show_dashboard": True,
    # Declarative, ORM-driven charts. When non-empty, these replace the default
    # demo charts on the dashboard. See docs "Charts from settings".
    # Each item: {id, kind, title, model, group_by, aggregate, field?, trunc?,
    #             filters?, limit?, size?}
    "charts": [],
    # Declarative stat cards (KPIs). Each item:
    # {label, model, aggregate, field?, filters?, icon?, trend?}
    "stat_cards": [],

    # --- HTMX ---
    "spa_navigation": True,
    "swap_target": "#ba-content",
}
