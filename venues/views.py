"""Views powering the venue booking workflow."""
from __future__ import annotations

from typing import Any

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Count
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import DetailView, FormView, ListView, TemplateView

from .filters import VenueFilter
from .forms import BookingForm, LoginForm, PaymentForm, RegistrationForm, ReviewForm
from .models import Booking, Payment, Review, Venue, Wishlist


class AuthLoginView(LoginView):
    template_name = "auth/login.html"
    authentication_form = LoginForm

    def get_success_url(self) -> str:
        return reverse("home")


class AuthLogoutView(LogoutView):
    next_page = reverse_lazy("auth:login")


class RegisterView(FormView):
    template_name = "auth/register.html"
    form_class = RegistrationForm
    success_url = reverse_lazy("auth:login")

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Registration successful. Please log in.")
        return super().form_valid(form)


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


class CatalogView(LoginRequiredMixin, ListView):
    model = Venue
    template_name = "catalog.html"
    context_object_name = "venues"
    paginate_by = 9

    def get_queryset(self):
        queryset = Venue.objects.select_related("category").prefetch_related("addons")
        self.filterset = VenueFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["filter"] = self.filterset
        context["wishlist_ids"] = set(
            Wishlist.objects.filter(user=self.request.user).values_list("venue_id", flat=True)
        )
        return context


class VenueDetailView(LoginRequiredMixin, DetailView):
    model = Venue
    template_name = "venue_detail.html"
    slug_field = "slug"
    context_object_name = "venue"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        venue: Venue = context["venue"]
        booking_form = BookingForm(self.request.POST or None)
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
        form = BookingForm(request.POST)
        if form.is_valid():
            booking: Booking = form.save(commit=False)
            booking.user = request.user
            booking.venue = self.object
            booking.save()
            form.save_m2m()
            messages.success(request, "Venue reserved! Continue to payment.")
            return redirect("payment", pk=booking.pk)
        messages.error(request, "Unable to create booking. Please check availability details.")
        return redirect("venue-detail", slug=self.object.slug)


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
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> JsonResponse:
        venue = get_object_or_404(Venue, pk=kwargs["pk"])
        wishlist, created = Wishlist.objects.get_or_create(user=request.user, venue=venue)
        if not created:
            wishlist.delete()
        return JsonResponse({"wishlisted": created})


class BookingPaymentView(LoginRequiredMixin, View):
    template_name = "booking_payment.html"

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        booking = get_object_or_404(
            Booking.objects.select_related("venue", "payment").prefetch_related("addons"), pk=pk, user=request.user
        )
        form = PaymentForm(instance=booking.payment)
        return render(request, self.template_name, {"booking": booking, "form": form})

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        booking = get_object_or_404(
            Booking.objects.select_related("venue", "payment").prefetch_related("addons"), pk=pk, user=request.user
        )
        form = PaymentForm(request.POST, instance=booking.payment)
        if form.is_valid():
            payment: Payment = form.save(commit=False)
            payment.status = "confirmed"
            payment.save()
            messages.success(request, "Payment confirmed! Enjoy your venue.")
            return redirect("home")
        messages.error(request, "Could not process the payment. Please try again.")
        return render(request, self.template_name, {"booking": booking, "form": form})


@login_required
def wishlist_toggle(request: HttpRequest, pk: int) -> JsonResponse:
    venue = get_object_or_404(Venue, pk=pk)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user, venue=venue)
    if not created:
        wishlist.delete()
    return JsonResponse({"wishlisted": created})


@login_required
def catalog_filter(request: HttpRequest) -> JsonResponse:
    filterset = VenueFilter(request.GET, queryset=Venue.objects.all())
    rendered_cards = [
        {
            "id": venue.id,
            "name": venue.name,
            "city": venue.city,
            "price": str(venue.price_per_hour),
            "category": venue.category.name,
            "image_url": venue.image_url,
            "url": reverse("venue-detail", kwargs={"slug": venue.slug}),
        }
        for venue in filterset.qs
    ]
    return JsonResponse({"venues": rendered_cards})
