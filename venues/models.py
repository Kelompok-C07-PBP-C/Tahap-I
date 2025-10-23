"""Database models for the venue booking domain."""
from __future__ import annotations

from decimal import Decimal
from datetime import time

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import slugify


class TimestampedModel(models.Model):
    """Abstract base model providing timestamp fields."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(TimestampedModel):
    """Represents a sports venue category."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.name


class Venue(TimestampedModel):
    """Venue model holding primary information."""

    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="venues")
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True)
    description = models.TextField()
    location = models.CharField(max_length=150)
    city = models.CharField(max_length=100)
    address = models.TextField(blank=True)
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.PositiveIntegerField(default=1)
    facilities = models.TextField(help_text="Comma separated facilities list.")
    image_url = models.URLField(blank=True)
    available_start_time = models.TimeField(default=time(7, 0))
    available_end_time = models.TimeField(default=time(22, 0))

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.name

    @property
    def facilities_list(self) -> list[str]:
        return [facility.strip() for facility in self.facilities.split(",") if facility.strip()]

    def hourly_total(self, hours: int) -> Decimal:
        return self.price_per_hour * Decimal(hours)


class AddOn(TimestampedModel):
    """Optional add-ons that can be purchased with a booking."""

    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name="addons")
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=9, decimal_places=2)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.name} ({self.venue.name})"


class VenueAvailability(TimestampedModel):
    """Represents a block of time when the venue is available for booking."""

    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name="availabilities")
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()

    class Meta:
        ordering = ["start_datetime"]
        verbose_name_plural = "Venue availabilities"

    def clean(self):  # pragma: no cover - requires Django validation
        if self.end_datetime <= self.start_datetime:
            raise ValidationError("End datetime must be greater than start datetime")


class Wishlist(TimestampedModel):
    """Stores a user's favourite venues."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wishlists")
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name="wishlisted_by")

    class Meta:
        unique_together = ("user", "venue")
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.user} ❤ {self.venue}"


class Booking(TimestampedModel):
    """Captures a user's booking details."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings")
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name="bookings")
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    addons = models.ManyToManyField(AddOn, related_name="bookings", blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-start_datetime"]

    def clean(self):  # pragma: no cover - requires Django validation
        if self.end_datetime <= self.start_datetime:
            raise ValidationError("End datetime must be greater than start datetime")

    @property
    def duration_hours(self) -> int:
        delta = self.end_datetime - self.start_datetime
        return int(delta.total_seconds() // 3600)

    @property
    def addons_total(self) -> Decimal:
        return sum((addon.price for addon in self.addons.all()), Decimal("0"))

    @property
    def base_cost(self) -> Decimal:
        return self.venue.hourly_total(self.duration_hours)

    @property
    def total_cost(self) -> Decimal:
        return self.base_cost + self.addons_total


class Payment(TimestampedModel):
    """Tracks payment status for a booking."""

    METHOD_CHOICES = [
        ("qris", "QRIS"),
        ("gopay", "GoPay"),
    ]

    STATUS_CHOICES = [
        ("waiting", "Waiting for confirmation"),
        ("confirmed", "Confirmed"),
        ("completed", "Completed"),
    ]

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name="payment")
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="waiting")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("10000"))
    reference_code = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"Payment {self.reference_code} ({self.get_status_display()})"


class Review(TimestampedModel):
    """A review left by a user for a venue."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("user", "venue")

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.user} rated {self.venue}"
