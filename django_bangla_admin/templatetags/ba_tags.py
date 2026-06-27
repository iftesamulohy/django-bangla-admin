"""Presentation template tags: menu, icons, active-state helpers."""

from django import template
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


@register.simple_tag
def ba_setting(key, default=""):
    return ba_conf(key, default)
