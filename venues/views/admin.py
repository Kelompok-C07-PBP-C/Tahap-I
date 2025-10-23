"""Admin workspace views."""
from __future__ import annotations

from typing import Any

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import inlineformset_factory
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, TemplateView

from ..forms import AddOnForm, AdminCreationForm, VenueForm
from ..models import AddOn, Booking, Payment, Venue
from .mixins import AdminRequiredMixin

AddOnFormSet = inlineformset_factory(Venue, AddOn, form=AddOnForm, extra=3, can_delete=True)


class AdminDashboardView(AdminRequiredMixin, LoginRequiredMixin, TemplateView):
    template_name = "admin/dashboard.html"
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
    template_name = "admin/venue_list.html"
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
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Venue created successfully.")
            return redirect("admin-venues")
        messages.error(request, "Please fix the errors below to create the venue.")
        self.object_list = self.get_queryset()
        return self.render_to_response(
            self.get_context_data(venue_form=form, show_create_modal=True)
        )


class AdminVenueCreateView(AdminRequiredMixin, LoginRequiredMixin, View):
    template_name = "admin/venue_form.html"
    success_url = reverse_lazy("admin-venues")

    def get(self, request: HttpRequest) -> HttpResponse:
        form = VenueForm()
        formset = AddOnFormSet(instance=Venue())
        return render(request, self.template_name, {"form": form, "formset": formset})

    def post(self, request: HttpRequest) -> HttpResponse:
        form = VenueForm(request.POST)
        formset = AddOnFormSet(request.POST, instance=form.instance)
        if form.is_valid() and formset.is_valid():
            venue = form.save()
            formset.instance = venue
            formset.save()
            messages.success(request, "Venue created successfully.")
            return redirect(self.success_url)
        messages.error(request, "Please fix the errors below to create the venue.")
        return render(request, self.template_name, {"form": form, "formset": formset})


class AdminVenueUpdateView(AdminRequiredMixin, LoginRequiredMixin, View):
    template_name = "admin/venue_form.html"
    success_url = reverse_lazy("admin-venues")

    def get_object(self, pk: int) -> Venue:
        return get_object_or_404(Venue, pk=pk)

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        venue = self.get_object(pk)
        form = VenueForm(instance=venue)
        formset = AddOnFormSet(instance=venue)
        return render(request, self.template_name, {"form": form, "formset": formset, "venue": venue})

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        venue = self.get_object(pk)
        form = VenueForm(request.POST, instance=venue)
        formset = AddOnFormSet(request.POST, instance=venue)
        if form.is_valid() and formset.is_valid():
            venue = form.save()
            formset.instance = venue
            formset.save()
            messages.success(request, "Venue updated successfully.")
            return redirect(self.success_url)
        messages.error(request, "Please correct the errors below.")
        return render(request, self.template_name, {"form": form, "formset": formset, "venue": venue})


class AdminVenueDeleteView(AdminRequiredMixin, LoginRequiredMixin, View):
    success_url = reverse_lazy("admin-venues")

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        venue = get_object_or_404(Venue, pk=pk)
        venue.delete()
        messages.success(request, "Venue deleted successfully.")
        return redirect(self.success_url)


class AdminBookingApprovalView(AdminRequiredMixin, LoginRequiredMixin, TemplateView):
    template_name = "admin/booking_approvals.html"

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
        booking = get_object_or_404(Booking.objects.select_related("payment"), pk=request.POST.get("booking_id"))
        decision = request.POST.get("decision")
        if booking.status != Booking.STATUS_PENDING:
            messages.error(request, "This booking has already been processed.")
            return redirect("admin-bookings")
        if decision == "approve":
            booking.approve(request.user)
            messages.success(request, "Booking approved successfully.")
        elif decision == "cancel":
            booking.cancel()
            if hasattr(booking, "payment"):
                booking.payment.status = "waiting"
                booking.payment.save(update_fields=["status", "updated_at"])
            messages.success(request, "Booking request cancelled.")
        else:
            messages.error(request, "Invalid action.")
        return redirect("admin-bookings")
