"""Template context processor injecting Bangla-admin config, language, theme.

Add ``"django_bangla_admin.context_processors.bangla_admin"`` to the template
``context_processors`` so non-admin templates (and admin templates rendered
outside ``each_context``) can read ``ba_*`` values.
"""

from django.utils import translation

from .conf import ba_conf

THEME_COOKIE = "ba_theme"


def bangla_admin(request):
    theme = request.COOKIES.get(THEME_COOKIE) or ba_conf("theme", "dark")
    if theme not in ("dark", "light"):
        theme = "dark"
    lang = translation.get_language() or ba_conf("default_language", "bn")
    return {
        "ba": ba_conf.as_dict(),
        "ba_theme": theme,
        "ba_lang": lang,
        "ba_is_htmx": request.headers.get("HX-Request") == "true",
    }
