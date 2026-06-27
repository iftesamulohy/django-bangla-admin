"""Sidebar menu builder.

Two modes:

* **Manual** — when ``BANGLA_ADMIN["menu"]`` is provided, items are taken from
  that list. Entries are either ``{"section": <label>}`` headers or links with
  ``label`` + (``url`` name or ``model`` "app.Model") + optional ``icon`` /
  ``badge``.
* **Auto** — when ``menu`` is ``None``, the menu is built from the models
  registered on the themed admin site, grouped by app, honoring permissions and
  ``hide_apps`` / ``hide_models``.

Every item is a plain dict consumed by ``templatetags/ba_tags.py`` and the
``_sidebar.html`` partial. Labels may be plain strings or ``{"bn", "en"}`` dicts
and are resolved at render time by ``ba_label``.
"""

from django.urls import NoReverseMatch, reverse

from .conf import ba_conf


def _resolve_model_url(model_key, site):
    """Return the changelist URL for an ``app_label.ModelName`` key, or None."""
    try:
        app_label, model_name = model_key.split(".")
    except ValueError:
        return None
    try:
        return reverse(
            f"{site.name}:{app_label}_{model_name.lower()}_changelist"
        )
    except NoReverseMatch:
        return None


def _icon_for(model_key, configured):
    icons = ba_conf("icons", {}) or {}
    return configured or icons.get(model_key) or ba_conf("default_icon", "circle-dot")


def _build_manual(menu_cfg, request, site):
    sections = []
    current = {"section": None, "items": []}
    for entry in menu_cfg:
        if "section" in entry:
            if current["items"] or current["section"] is not None:
                sections.append(current)
            current = {"section": entry["section"], "items": []}
            continue

        url = None
        active_url_name = entry.get("url")
        if active_url_name:
            try:
                url = reverse(active_url_name)
            except NoReverseMatch:
                url = active_url_name if active_url_name.startswith("/") else None
        elif entry.get("model"):
            url = _resolve_model_url(entry["model"], site)

        if url is None and entry.get("model"):
            # Model not registered / no permission -> skip silently.
            continue

        current["items"].append({
            "label": entry.get("label", ""),
            "icon": _icon_for(entry.get("model"), entry.get("icon")),
            "url": url or "#",
            "badge": entry.get("badge"),
        })
    if current["items"] or current["section"] is not None:
        sections.append(current)
    return sections


def _build_auto(request, site):
    """Build menu from the admin app list (respects permissions)."""
    app_list = site.get_app_list(request)
    hide_apps = set(ba_conf("hide_apps", []) or [])
    hide_models = set(ba_conf("hide_models", []) or [])
    icons = ba_conf("icons", {}) or {}

    sections = []
    for app in app_list:
        if app["app_label"] in hide_apps:
            continue
        items = []
        for model in app["models"]:
            model_key = f"{app['app_label']}.{model['object_name']}"
            if model_key in hide_models:
                continue
            items.append({
                "label": model["name"],
                "icon": icons.get(model_key, ba_conf("default_icon", "circle-dot")),
                "url": model.get("admin_url") or "#",
                "badge": None,
            })
        if items:
            sections.append({"section": app["name"], "items": items})
    return sections


def build_menu(request, site):
    """Return the resolved sidebar structure for the current request."""
    if not ba_conf("show_sidebar", True):
        return []

    menu_cfg = ba_conf("menu")
    if menu_cfg:
        return _build_manual(menu_cfg, request, site)
    return _build_auto(request, site)
