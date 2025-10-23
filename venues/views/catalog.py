"""Catalog listing views."""
from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, JsonResponse
from django.urls import reverse
from django.utils.text import Truncator
from django.views.generic import ListView

from ..filters import VenueFilter
from ..models import Venue, Wishlist
from .mixins import EnsureCsrfCookieMixin


class CatalogView(EnsureCsrfCookieMixin, LoginRequiredMixin, ListView):
    model = Venue
    template_name = "catalog.html"
    context_object_name = "venues"
    paginate_by = 9

    def get_queryset(self):
        queryset = Venue.objects.select_related("category").prefetch_related("addons")
        self.filterset = VenueFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter"] = self.filterset
        context["wishlist_ids"] = set(
            Wishlist.objects.filter(user=self.request.user).values_list("venue_id", flat=True)
        )
        return context


@login_required
def catalog_filter(request: HttpRequest) -> JsonResponse:
    filterset = VenueFilter(request.GET, queryset=Venue.objects.all())
    wishlist_ids = set(
        Wishlist.objects.filter(user=request.user).values_list("venue_id", flat=True)
    )
    rendered_cards = [
        {
            "id": venue.id,
            "name": venue.name,
            "city": venue.city,
            "price": str(venue.price_per_hour),
            "category": venue.category.name,
            "image_url": venue.image_url,
            "url": reverse("venue-detail", kwargs={"slug": venue.slug}),
            "description": Truncator(venue.description).chars(120),
            "wishlisted": venue.id in wishlist_ids,
        }
        for venue in filterset.qs
    ]
    return JsonResponse({"venues": rendered_cards})
