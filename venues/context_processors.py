"""Custom context processors for global template data."""
from __future__ import annotations

from django.conf import settings
from django.middleware.csrf import get_token

from .forms import SearchFilterForm


def global_filters(request):
    """Provide the search filter form globally for navigation search bars."""

    return {
        "global_filter_form": SearchFilterForm(request.GET or None),
    }


def csrf_token_context(request):
    """Expose the CSRF cookie value so templates can embed it for JavaScript."""

    token = request.COOKIES.get(settings.CSRF_COOKIE_NAME)
    if not token:
        token = request.META.get("CSRF_COOKIE") or get_token(request)
    return {
        "csrf_cookie_value": token,
    }
