"""Wishlist related views."""
from __future__ import annotations

from typing import Any

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.text import Truncator
from django.views import View
from django.views.generic import ListView

from ..models import Booking, Venue, Wishlist
from .mixins import EnsureCsrfCookieMixin


class WishlistView(EnsureCsrfCookieMixin, LoginRequiredMixin, ListView):
    template_name = "wishlist.html"
    context_object_name = "wishlists"

    def get_queryset(self):
        return (
            Wishlist.objects.filter(user=self.request.user)
            .select_related("venue", "venue__category")
            .prefetch_related("venue__addons")
        )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["approved_bookings"] = (
            Booking.objects.filter(user=self.request.user, status=Booking.STATUS_ACTIVE)
            .select_related("venue")
            .prefetch_related("addons")
            .order_by("-start_datetime")
        )
        return context


class WishlistToggleView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> JsonResponse:  # type: ignore[override]
        venue = get_object_or_404(Venue, pk=kwargs["pk"])
        wishlist, created = Wishlist.objects.get_or_create(user=request.user, venue=venue)
        if not created:
            wishlist.delete()
        return JsonResponse(_build_wishlist_response(request, venue, created))


@login_required
def wishlist_toggle(request: HttpRequest, pk: int) -> JsonResponse:
    venue = get_object_or_404(Venue, pk=pk)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user, venue=venue)
    if not created:
        wishlist.delete()
    return JsonResponse(_build_wishlist_response(request, venue, created))


def _build_wishlist_response(request: HttpRequest, venue: Venue, wishlisted: bool) -> dict[str, Any]:
    description = Truncator(venue.description or "").chars(120)
    venue_data = {
        "id": str(venue.pk),
        "name": venue.name,
        "city": venue.city,
        "category": venue.category.name if venue.category else "",
        "price": str(venue.price_per_hour),
        "url": reverse("venue-detail", kwargs={"slug": venue.slug}),
        "image": venue.image_url,
        "description": description,
        "toggle_url": reverse("wishlist-toggle-api", kwargs={"pk": venue.pk}),
    }
    response: dict[str, Any] = {
        "wishlisted": wishlisted,
        "wishlist_count": Wishlist.objects.filter(user=request.user).count(),
        "venue": venue_data,
        "wishlist_item_html": None,
    }
    if wishlisted:
        response["wishlist_item_html"] = render_to_string(
            "partials/wishlist_card.html",
            {"venue": venue, "wishlist_description": description},
            request=request,
        )
    return response
