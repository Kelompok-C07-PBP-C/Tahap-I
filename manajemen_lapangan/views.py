"""Admin workspace views for managing venues."""
from __future__ import annotations

import json
import logging
from typing import Any

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import ListView, TemplateView

from authentication.forms import AdminCreationForm
from authentication.mixins import AdminRequiredMixin
from add_on.formsets import build_addon_formset
from rent.models import Booking, Payment

from .forms import BookingDecisionForm, VenueForm
from .models import Venue

logger = logging.getLogger(__name__)


class AdminDashboardView(AdminRequiredMixin, LoginRequiredMixin, TemplateView):
    template_name = "manajemen_lapangan/dashboard.html"
    form_class = AdminCreationForm

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        user_model = get_user_model()
        context.update(
            {
                "stats": {
                    "venues": Venue.objects.count(),
                    "bookings": Booking.objects.count(),
                    "payments": Payment.objects.count(),
                    "pending_bookings": Booking.objects.filter(status=Booking.STATUS_PENDING).count(),
                },
                "admins": user_model.objects.filter(is_staff=True).order_by("username"),
                "admin_form": kwargs.get("admin_form") or self.form_class(),
            }
        )
        return context

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "New admin account created successfully.")
            return redirect("admin-dashboard")
        messages.error(request, "Unable to create admin. Please correct the errors below.")
        return self.render_to_response(self.get_context_data(admin_form=form))


class AdminVenueListView(AdminRequiredMixin, LoginRequiredMixin, ListView):
    model = Venue
    template_name = "manajemen_lapangan/venue_list.html"
    context_object_name = "venues"
    paginate_by = 10
    ordering = ["name"]
    form_class = VenueForm

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.setdefault("venue_form", kwargs.get("venue_form") or self.form_class())
        context["show_create_modal"] = kwargs.get("show_create_modal") or self.request.GET.get("show") == "create"
        return context

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if not request.user.has_perm("manajemen_lapangan.add_venue"):
            messages.error(request, "You do not have permission to create venues.")
            return redirect("admin-venues")

        form = self.form_class(request.POST)
        if form.is_valid():
            try:
                form.save()
            except IntegrityError:
                form.add_error(
                    "slug",
                    "Slug venue ini sudah digunakan. Gunakan nama atau slug lain.",
                )
            else:
                messages.success(request, "Venue created successfully.")
                return redirect("admin-venues")
        messages.error(request, "Please fix the errors below to create the venue.")
        self.object_list = self.get_queryset()
        return self.render_to_response(
            self.get_context_data(venue_form=form, show_create_modal=True)
        )


class AdminVenueCreateView(AdminRequiredMixin, LoginRequiredMixin, View):
    template_name = "manajemen_lapangan/venue_form.html"
    success_url = reverse_lazy("admin-venues")

    def get(self, request: HttpRequest) -> HttpResponse:
        form = VenueForm()
        formset = build_addon_formset(instance=form.instance)
        return render(request, self.template_name, {"form": form, "formset": formset})

    def post(self, request: HttpRequest) -> HttpResponse:
        if not request.user.has_perm("manajemen_lapangan.add_venue"):
            messages.error(request, "You do not have permission to create venues.")
            return redirect(self.success_url)

        form = VenueForm(request.POST)
        formset = build_addon_formset(data=request.POST, instance=form.instance)
        if form.is_valid() and formset.is_valid():
            try:
                venue = form.save()
            except IntegrityError:
                form.add_error(
                    "slug",
                    "Slug venue ini sudah digunakan. Gunakan nama atau slug lain.",
                )
            else:
                formset.instance = venue
                formset.save()
                messages.success(request, "Venue created successfully.")
                return redirect(self.success_url)
        messages.error(request, "Please fix the errors below to create the venue.")
        return render(request, self.template_name, {"form": form, "formset": formset})


class AdminVenueUpdateView(AdminRequiredMixin, LoginRequiredMixin, View):
    template_name = "manajemen_lapangan/venue_form.html"
    success_url = reverse_lazy("admin-venues")

    def get_object(self, pk: int) -> Venue:
        return get_object_or_404(Venue, pk=pk)

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        venue = self.get_object(pk)
        form = VenueForm(instance=venue)
        formset = build_addon_formset(instance=venue)
        return render(request, self.template_name, {"form": form, "formset": formset, "venue": venue})

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        venue = self.get_object(pk)
        form = VenueForm(request.POST, instance=venue)
        formset = build_addon_formset(data=request.POST, instance=venue)
        if form.is_valid() and formset.is_valid():
            try:
                venue = form.save()
            except IntegrityError:
                form.add_error(
                    "slug",
                    "Slug venue ini sudah digunakan. Gunakan nama atau slug lain.",
                )
            else:
                formset.instance = venue
                formset.save()
                messages.success(request, "Venue updated successfully.")
                return redirect(self.success_url)
        messages.error(request, "Please correct the errors below.")
        return render(request, self.template_name, {"form": form, "formset": formset, "venue": venue})


class AdminVenueDeleteView(AdminRequiredMixin, LoginRequiredMixin, View):
    success_url = reverse_lazy("admin-venues")

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        if not request.user.has_perm("manajemen_lapangan.delete_venue"):
            messages.error(request, "You do not have permission to delete venues.")
            return redirect(self.success_url)

        venue = get_object_or_404(Venue, pk=pk)
        venue.delete()
        messages.success(request, "Venue deleted successfully.")
        return redirect(self.success_url)


class AdminBookingApprovalView(AdminRequiredMixin, LoginRequiredMixin, TemplateView):
    template_name = "manajemen_lapangan/booking_approvals.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["pending_bookings"] = (
            Booking.objects.select_related("venue", "user")
            .prefetch_related("addons")
            .filter(status=Booking.STATUS_PENDING)
            .order_by("start_datetime")
        )
        return context

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        form = BookingDecisionForm(request.POST)

        if not form.is_valid():
            error_messages = list(form.non_field_errors())
            for field_errors in form.errors.values():
                error_messages.extend(field_errors)
            if not error_messages:
                error_messages.append("Unable to process the booking request.")
            for error in error_messages:
                messages.error(request, error)
            return redirect("admin-bookings")

        _, decision = form.apply_decision(request.user)
        if decision == BookingDecisionForm.APPROVE:
            messages.success(request, "Booking approved successfully.")
        else:
            messages.success(request, "Booking request cancelled.")
        return redirect("admin-bookings")


def serialize_venue(venue: Venue) -> dict[str, Any]:
    """Return a JSON-serialisable representation of a venue."""

    return {
        "id": venue.pk,
        "name": venue.name,
        "slug": venue.slug,
        "description": venue.description,
        "location": venue.location,
        "city": venue.city,
        "address": venue.address,
        "price_per_hour": str(venue.price_per_hour),
        "capacity": venue.capacity,
        "facilities": venue.facilities,
        "image_url": venue.image_url,
        "available_start_time": venue.available_start_time.strftime("%H:%M"),
        "available_end_time": venue.available_end_time.strftime("%H:%M"),
        "category": {
            "id": venue.category_id,
            "name": venue.category.name,
        },
        "detail_url": reverse("venue-detail", kwargs={"slug": venue.slug}),
        "edit_url": reverse("admin-venue-edit", kwargs={"pk": venue.pk}),
        "delete_url": reverse("admin-venue-delete", kwargs={"pk": venue.pk}),
    }


def build_form_errors(form: VenueForm) -> dict[str, list[str]]:
    """Normalise Django form errors for JSON responses."""

    error_data: dict[str, list[str]] = {}
    for field, errors in form.errors.get_json_data().items():
        error_data[field] = [entry.get("message", "") for entry in errors]
    return error_data


def is_ajax(request: HttpRequest) -> bool:
    return request.headers.get("x-requested-with") == "XMLHttpRequest"


class AdminVenueApiView(AdminRequiredMixin, LoginRequiredMixin, View):
    """Provide JSON CRUD operations for venues."""

    http_method_names = ["get", "post"]

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return super().dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest) -> JsonResponse:
        if not is_ajax(request):
            return JsonResponse({"success": False, "error": "AJAX request required."}, status=400)

        venues = (
            Venue.objects.select_related("category")
            .order_by("name")
        )
        payload = [serialize_venue(venue) for venue in venues]
        return JsonResponse({"success": True, "venues": payload})

    def post(self, request: HttpRequest) -> JsonResponse:
        if not is_ajax(request):
            return JsonResponse({"success": False, "error": "AJAX request required."}, status=400)

        if not request.user.has_perm("manajemen_lapangan.add_venue"):
            return JsonResponse({"success": False, "error": "Permission denied."}, status=403)

        data = self._extract_payload(request)
        form = VenueForm(data)
        if form.is_valid():
            venue = form.save()
            return JsonResponse({"success": True, "venue": serialize_venue(venue)})
        return JsonResponse({"success": False, "errors": build_form_errors(form)}, status=400)

    def _extract_payload(self, request: HttpRequest) -> dict[str, Any]:
        if request.content_type and "application/json" in request.content_type:
            try:
                payload = json.loads(request.body.decode("utf-8") or "{}")
            except json.JSONDecodeError:
                return {}
            return {key: value for key, value in payload.items() if value is not None}
        return request.POST.dict()


class AdminVenueDetailApiView(AdminRequiredMixin, LoginRequiredMixin, View):
    """Handle JSON operations for a single venue."""

    http_method_names = ["get", "put", "patch", "delete"]

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, pk: int) -> Venue:
        return get_object_or_404(Venue.objects.select_related("category"), pk=pk)

    def get(self, request: HttpRequest, pk: int) -> JsonResponse:
        if not is_ajax(request):
            return JsonResponse({"success": False, "error": "AJAX request required."}, status=400)

        venue = self.get_object(pk)
        return JsonResponse({"success": True, "venue": serialize_venue(venue)})

    def put(self, request: HttpRequest, pk: int) -> JsonResponse:
        return self._update(request, pk)

    def patch(self, request: HttpRequest, pk: int) -> JsonResponse:
        return self._update(request, pk)

    def delete(self, request: HttpRequest, pk: int) -> JsonResponse:
        if not is_ajax(request):
            return JsonResponse({"success": False, "error": "AJAX request required."}, status=400)

        if not request.user.has_perm("manajemen_lapangan.delete_venue"):
            return JsonResponse({"success": False, "error": "Permission denied."}, status=403)

        venue = self.get_object(pk)
        venue.delete()
        return JsonResponse({"success": True})

    def _update(self, request: HttpRequest, pk: int) -> JsonResponse:
        if not is_ajax(request):
            return JsonResponse({"success": False, "error": "AJAX request required."}, status=400)

        if not request.user.has_perm("manajemen_lapangan.change_venue"):
            return JsonResponse({"success": False, "error": "Permission denied."}, status=403)

        venue = self.get_object(pk)
        data = self._extract_payload(request)
        form = VenueForm(data, instance=venue)
        if form.is_valid():
            venue = form.save()
            venue.refresh_from_db()
            return JsonResponse({"success": True, "venue": serialize_venue(venue)})
        return JsonResponse({"success": False, "errors": build_form_errors(form)}, status=400)

    def _extract_payload(self, request: HttpRequest) -> dict[str, Any]:
        if request.content_type and "application/json" in request.content_type:
            try:
                payload = json.loads(request.body.decode("utf-8") or "{}")
            except json.JSONDecodeError:
                return {}
            return {key: value for key, value in payload.items() if value is not None}
        return request.POST.dict()
