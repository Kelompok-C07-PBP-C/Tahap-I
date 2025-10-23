"""Landing page views."""
from __future__ import annotations

from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.views.generic import TemplateView

from ..filters import VenueFilter
from ..models import Venue, Wishlist


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        venue_filter = VenueFilter(self.request.GET, queryset=Venue.objects.all())
        popular_venues = (
            Venue.objects.annotate(bookings_count=Count("bookings"))
            .order_by("-bookings_count")
            .prefetch_related("addons")[:3]
        )
        context.update(
            {
                "filter": venue_filter,
                "venues": venue_filter.qs[:6],
                "popular_venues": popular_venues,
                "wishlist_ids": set(
                    Wishlist.objects.filter(user=self.request.user).values_list("venue_id", flat=True)
                ),
            }
        )
        return context
