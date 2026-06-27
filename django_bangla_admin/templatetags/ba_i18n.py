"""i18n template helpers: dict-label resolution and Bangla numerals."""

from django import template
from django.utils import translation

from ..conf import ba_conf

register = template.Library()

# Western digit -> Bengali digit map.
_BN_DIGITS = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")


def resolve_label(value, lang=None):
    """Resolve a string or ``{"bn", "en"}`` dict to the active language."""
    if isinstance(value, dict):
        lang = lang or translation.get_language() or ba_conf("default_language", "bn")
        short = lang.split("-")[0]
        return value.get(short) or value.get("en") or next(iter(value.values()), "")
    return value


@register.simple_tag
def ba_label(value):
    """Resolve a (possibly dict) label for the current language."""
    return resolve_label(value)


@register.filter(name="ba_label")
def ba_label_filter(value):
    return resolve_label(value)


@register.filter(name="bn_number")
def bn_number(value):
    """Convert Western digits to Bengali numerals when lang == bn (if enabled)."""
    if not ba_conf("bangla_numerals", True):
        return value
    lang = (translation.get_language() or "").split("-")[0]
    if lang != "bn":
        return value
    try:
        return str(value).translate(_BN_DIGITS)
    except (TypeError, ValueError):
        return value
