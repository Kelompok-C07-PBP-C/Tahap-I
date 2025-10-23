"""Wishlist related views."""
from __future__ import annotations

from typing import Any

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.generic import ListView

from ..models import Venue, Wishlist


class WishlistView(LoginRequiredMixin, ListView):
    template_name = "wishlist.html"
    context_object_name = "wishlists"

    def get_queryset(self):
        return (
            Wishlist.objects.filter(user=self.request.user)
            .select_related("venue", "venue__category")
            .prefetch_related("venue__addons")
        )


class WishlistToggleView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> JsonResponse:  # type: ignore[override]
        venue = get_object_or_404(Venue, pk=kwargs["pk"])
        wishlist, created = Wishlist.objects.get_or_create(user=request.user, venue=venue)
        if not created:
            wishlist.delete()
        return JsonResponse({"wishlisted": created})


@login_required
def wishlist_toggle(request: HttpRequest, pk: int) -> JsonResponse:
    venue = get_object_or_404(Venue, pk=pk)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user, venue=venue)
    if not created:
        wishlist.delete()
    return JsonResponse({"wishlisted": created})
