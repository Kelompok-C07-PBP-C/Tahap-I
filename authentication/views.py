"""Authentication views."""
from __future__ import annotations

from typing import Any

from django.contrib import messages
from django.contrib.auth import login as auth_login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.db.models import Count
from django.forms.forms import NON_FIELD_ERRORS
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import FormView, TemplateView

from interaksi.models import Wishlist
from katalog.filters import VenueFilter
from manajemen_lapangan.models import Venue
from rent.models import Booking, Payment

from .forms import LoginForm, RegistrationForm
from .mixins import AdminRequiredMixin, EnsureCsrfCookieMixin


class AuthLoginView(EnsureCsrfCookieMixin, LoginView):
    template_name = "authentication/login.html"
    authentication_form = LoginForm

    def get_success_url(self) -> str:
        return reverse("home")

    def _is_ajax_request(self) -> bool:
        request_header = self.request.headers.get("X-Requested-With", "")
        return request_header.lower() == "xmlhttprequest"

    def form_valid(self, form):
        if self._is_ajax_request():
            auth_login(self.request, form.get_user())
            return JsonResponse(
                {
                    "success": True,
                    "redirect_url": self.get_success_url(),
                }
            )
        return super().form_valid(form)

    def form_invalid(self, form):
        if self._is_ajax_request():
            error_data = form.errors.get_json_data()
            field_errors: dict[str, list[str]] = {}
            non_field_errors: list[str] = []

            for field, messages in error_data.items():
                parsed_messages = [message.get("message", "") for message in messages]
                if field == NON_FIELD_ERRORS:
                    non_field_errors.extend(parsed_messages)
                    continue
                field_errors[field] = parsed_messages

            return JsonResponse(
                {
                    "success": False,
                    "errors": field_errors,
                    "non_field_errors": non_field_errors,
                },
                status=400,
            )
        return super().form_invalid(form)


class AuthLogoutView(LoginRequiredMixin, View):
    """Log out the current user and redirect them to the login page."""

    success_url = reverse_lazy("authentication:login")

    def _logout(self, request: HttpRequest) -> None:
        logout(request)
        messages.success(request, "You have been logged out successfully.")

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self._logout(request)
        return redirect(self.success_url)

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        return self.post(request, *args, **kwargs)


class RegisterView(FormView):
    template_name = "authentication/register.html"
    form_class = RegistrationForm
    success_url = reverse_lazy("authentication:login")

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Registration successful. Please log in.")
        return super().form_valid(form)


class HomeView(EnsureCsrfCookieMixin, TemplateView):
    template_name = "authentication/home.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        venue_filter = VenueFilter(self.request.GET, queryset=Venue.objects.all())
        popular_venues = (
            Venue.objects.annotate(bookings_count=Count("bookings"))
            .order_by("-bookings_count")
            .prefetch_related("addons")[:3]
        )
        wishlist_ids: set[int] = set()
        if self.request.user.is_authenticated:
            wishlist_ids = set(
                Wishlist.objects.filter(user=self.request.user).values_list("venue_id", flat=True)
            )
        context.update(
            {
                "filter": venue_filter,
                "venues": venue_filter.qs[:6],
                "popular_venues": popular_venues,
                "wishlist_ids": wishlist_ids,
            }
        )
        return context


class UserLandingView(LoginRequiredMixin, TemplateView):
    template_name = "authentication/user_dashboard.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "active_bookings": Booking.objects.filter(
                    user=self.request.user,
                    status__in=[
                        Booking.STATUS_ACTIVE,
                        Booking.STATUS_CONFIRMED,
                        Booking.STATUS_COMPLETED,
                    ],
                ).select_related("venue"),
                "wishlist_count": Wishlist.objects.filter(user=self.request.user).count(),
            }
        )
        return context


class AdminLandingView(AdminRequiredMixin, LoginRequiredMixin, TemplateView):
    template_name = "authentication/admin_dashboard.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "total_venues": Venue.objects.count(),
                "pending_bookings": Booking.objects.filter(status=Booking.STATUS_PENDING).count(),
                "confirmed_payments": Payment.objects.filter(status="confirmed").count(),
            }
        )
        return context
