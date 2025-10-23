"""Domain signals for keeping related entities in sync."""
from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

from .models import Booking, Payment


@receiver(post_save, sender=Booking)
def ensure_payment_for_booking(sender, instance: Booking, created: bool, **kwargs):
    """Ensure a payment record exists whenever a booking is created."""

    if created:
        total = instance.total_cost if instance.pk else Decimal("0")
        Payment.objects.create(
            booking=instance,
            method="qris",
            total_amount=total,
            deposit_amount=Decimal("10000"),
            reference_code=uuid4().hex[:12].upper(),
        )
    else:
        if hasattr(instance, "payment"):
            instance.payment.total_amount = instance.total_cost
            instance.payment.save(update_fields=["total_amount", "updated_at"])


@receiver(m2m_changed, sender=Booking.addons.through)
def update_payment_on_addons(sender, instance: Booking, action: str, **kwargs):
    """Recalculate payment totals when add-ons are modified."""

    if action in {"post_add", "post_remove", "post_clear"} and hasattr(instance, "payment"):
        instance.payment.total_amount = instance.total_cost
        instance.payment.save(update_fields=["total_amount", "updated_at"])
