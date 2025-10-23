"""Booking and payment flow views."""
from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from ..forms import PaymentForm
from ..models import Booking, Payment


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
