"""Cookie-based language switching (Django 4.2+ correct: no session key).

The topbar segmented toggle fires ``hx-get`` to this view. We set the language
cookie that ``LocaleMiddleware`` reads on subsequent requests, then return a
204 with an ``HX-Refresh`` (full chrome re-render) so the font stack and all
translated strings update. (A 204 + HX-Refresh keeps the client logic trivial
and guarantees the new ``<html lang>`` / font stack apply.)
"""

from django.conf import settings
from django.http import HttpResponse
from django.utils import translation


def set_language(request):
    lang = request.GET.get("lang") or request.POST.get("lang") or settings.LANGUAGE_CODE
    if lang not in dict(settings.LANGUAGES):
        lang = settings.LANGUAGE_CODE

    translation.activate(lang)

    if request.headers.get("HX-Request") == "true":
        response = HttpResponse(status=204)
        response["HX-Refresh"] = "true"
    else:
        next_url = request.GET.get("next") or request.META.get("HTTP_REFERER") or "/"
        from django.http import HttpResponseRedirect
        response = HttpResponseRedirect(next_url)

    response.set_cookie(
        settings.LANGUAGE_COOKIE_NAME,
        lang,
        max_age=365 * 24 * 3600,
        samesite="Lax",
    )
    return response
