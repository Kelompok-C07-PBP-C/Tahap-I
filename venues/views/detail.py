"""Product detail view and interactions."""
from __future__ import annotations

from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.views.generic import DetailView

from ..forms import BookingForm, ReviewForm
from ..models import Booking, Review, Venue, Wishlist
from .mixins import EnsureCsrfCookieMixin


class VenueDetailView(EnsureCsrfCookieMixin, LoginRequiredMixin, DetailView):
    model = Venue
    template_name = "venue_detail.html"
    slug_field = "slug"
    context_object_name = "venue"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        venue: Venue = context["venue"]
        booking_form = BookingForm(self.request.POST or None, venue=venue)
        review_form = ReviewForm(self.request.POST or None)
        context.update(
            {
                "booking_form": booking_form,
                "review_form": review_form,
                "wishlist_ids": set(
                    Wishlist.objects.filter(user=self.request.user).values_list("venue_id", flat=True)
                ),
                "reviews": venue.reviews.select_related("user"),
            }
        )
        return context

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        self.object = self.get_object()
        if "submit_review" in request.POST:
            return self.handle_review(request)
        return self.handle_booking(request)

    def handle_review(self, request: HttpRequest) -> HttpResponse:
        form = ReviewForm(request.POST)
        if form.is_valid():
            Review.objects.update_or_create(
                user=request.user,
                venue=self.object,
                defaults=form.cleaned_data,
            )
            messages.success(request, "Your review has been saved.")
        else:
            messages.error(request, "Unable to save review. Please check the form.")
        return redirect("venue-detail", slug=self.object.slug)

    def handle_booking(self, request: HttpRequest) -> HttpResponse:
        form = BookingForm(request.POST, venue=self.object)
        if form.is_valid():
            booking: Booking = form.save(commit=False)
            booking.user = request.user
            booking.venue = self.object
            booking.save()
            form.save_m2m()
            messages.success(
                request,
                "Your booking request was submitted and is awaiting admin approval.",
            )
            return redirect("booked-places")
        messages.error(request, "Unable to create booking. Please check availability details.")
        return redirect("venue-detail", slug=self.object.slug)
