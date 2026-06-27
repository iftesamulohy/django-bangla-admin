"""HTMX-aware middleware.

When a request carries the ``HX-Request`` header we want to return only the
inner content region, not the full sidebar+topbar shell. Django's admin views
(change_list, change_form, etc.) render a complete page, so this middleware
extracts the content block from the rendered HTML for HTMX requests.

The themed ``base.html`` wraps its main region between the markers
``<!--ba:content:start-->`` and ``<!--ba:content:end-->``. For HTMX requests we
return just that slice, letting HTMX swap it into ``#ba-content``.
"""

from django.utils.deprecation import MiddlewareMixin

from .conf import ba_conf

CONTENT_START = b"<!--ba:content:start-->"
CONTENT_END = b"<!--ba:content:end-->"


class HtmxShellMiddleware(MiddlewareMixin):
    """Strip the outer shell from admin responses for HTMX navigation."""

    def process_response(self, request, response):
        if not ba_conf("spa_navigation", True):
            return response
        if request.headers.get("HX-Request") != "true":
            return response
        # Boosted full-page forms set HX-Boosted; still strip the shell.
        content_type = response.get("Content-Type", "")
        if "text/html" not in content_type:
            return response
        if getattr(response, "streaming", False):
            return response

        body = response.content
        start = body.find(CONTENT_START)
        end = body.find(CONTENT_END)
        if start == -1 or end == -1 or end < start:
            return response

        inner = body[start + len(CONTENT_START):end]
        response.content = inner
        if response.has_header("Content-Length"):
            response["Content-Length"] = str(len(response.content))
        return response
