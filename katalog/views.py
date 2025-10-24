"""User facing catalog views."""
from __future__ import annotations

from typing import Any

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.text import Truncator
from django.views.generic import DetailView, ListView

from authentication.mixins import EnsureCsrfCookieMixin
from interaksi.forms import ReviewForm
from interaksi.models import Review, Wishlist
from manajemen_lapangan.models import Venue
from rent.forms import BookingForm
from rent.models import Booking

from .filters import VenueFilter


class CatalogView(EnsureCsrfCookieMixin, LoginRequiredMixin, ListView):
    model = Venue
    template_name = "katalog/catalog.html"
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
            "toggle_url": reverse("wishlist-toggle-api", args=[venue.id]),
        }
        for venue in filterset.qs
    ]
    return JsonResponse({"venues": rendered_cards})


class VenueDetailView(EnsureCsrfCookieMixin, LoginRequiredMixin, DetailView):
    model = Venue
    template_name = "katalog/venue_detail.html"
    slug_field = "slug"
    context_object_name = "venue"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        venue: Venue = context["venue"]
        can_book = not self.request.user.is_staff
        booking_form = None
        if can_book:
            booking_form = BookingForm(self.request.POST or None, venue=venue)
        review_form = ReviewForm(self.request.POST or None)
        context.update(
            {
                "booking_form": booking_form,
                "review_form": review_form,
                "can_book": can_book,
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
        if request.user.is_staff:
            messages.error(
                request,
                "Administrators cannot create bookings. Please use a regular user account.",
            )
            return redirect("venue-detail", slug=self.object.slug)
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
