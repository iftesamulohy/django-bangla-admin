"""Presentation template tags: menu, icons, active-state helpers."""

from django import template
from django.urls import NoReverseMatch, reverse
from django.utils.safestring import mark_safe

from ..conf import ba_conf
from ..icons import get_icon_svg

register = template.Library()


@register.inclusion_tag("django_bangla_admin/partials/_sidebar.html", takes_context=True)
def ba_menu(context):
    """Render the sidebar menu using the context's ``ba_menu`` structure."""
    request = context.get("request")
    return {
        "ba_menu": context.get("ba_menu", []),
        "request": request,
        "current_path": request.path if request else "",
        "ba": ba_conf.as_dict(),
    }


@register.simple_tag
def ba_icon(name, cls="ba-icon"):
    """Inline an SVG icon by Lucide-style name."""
    return mark_safe(get_icon_svg(name, cls=cls))


@register.simple_tag(takes_context=True)
def ba_is_active(context, url):
    """Return 'active' if ``url`` matches the current request path."""
    request = context.get("request")
    if not request or not url or url == "#":
        return ""
    path = request.path
    if url == "/":
        return "active" if path == "/" else ""
    return "active" if path.startswith(url) else ""


@register.simple_tag(takes_context=True)
def ba_tree_open(context, item):
    """Return ' is-open' when a tree group holds the active child link."""
    request = context.get("request")
    if not request:
        return ""
    path = request.path
    for child in item.get("children", []):
        url = child.get("url")
        if url and url != "#" and path.startswith(url):
            return " is-open"
    return ""


@register.simple_tag
def ba_setting(key, default=""):
    return ba_conf(key, default)


@register.inclusion_tag(
    "django_bangla_admin/partials/_result_list.html", takes_context=True
)
def ba_result_list(context, cl):
    """Render the changelist results table with a per-row actions column.

    Wraps Django's stock ``result_list`` tag (so cell rendering, sorting
    headers and editable formsets keep working) and pairs each rendered row
    with permission-checked edit / delete URLs for the row's object.
    """
    from django.contrib.admin.templatetags.admin_list import (
        result_list as dj_result_list,
    )

    base = dj_result_list(cl)
    request = context.get("request")
    opts = cl.model._meta
    model_admin = cl.model_admin
    site_name = model_admin.admin_site.name

    def _url(action, obj):
        try:
            return reverse(
                f"{site_name}:{opts.app_label}_{opts.model_name}_{action}",
                args=[obj.pk],
            )
        except NoReverseMatch:
            return None

    rows = []
    show_actions = False
    for obj, cells in zip(cl.result_list, base["results"]):
        change_url = _url("change", obj) if model_admin.has_change_permission(request, obj) else None
        delete_url = _url("delete", obj) if model_admin.has_delete_permission(request, obj) else None
        if change_url or delete_url:
            show_actions = True
        rows.append({
            "cells": list(cells),
            "form": getattr(cells, "form", None),
            "change_url": change_url,
            "delete_url": delete_url,
        })

    base["ba_rows"] = rows
    base["ba_show_actions"] = show_actions
    base["request"] = request
    return base
