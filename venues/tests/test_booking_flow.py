from __future__ import annotations

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from venues.models import AddOn, Booking, Category, Venue


class BookingFlowTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="booker",
            email="booker@example.com",
            password="secret123",
        )
        self.category = Category.objects.create(name="Stadium")
        self.venue = Venue.objects.create(
            category=self.category,
            name="Skyline Arena",
            description="Indoor multi-purpose arena.",
            location="Central",
            city="Metropolis",
            address="1 Arena Way",
            price_per_hour="150000.00",
            capacity=1500,
            facilities="Lighting, Seating",
            image_url="https://example.com/arena.jpg",
        )
        self.addon = AddOn.objects.create(
            venue=self.venue,
            name="Premium lighting",
            description="Enhanced lighting package",
            price="50000.00",
        )

    def test_user_can_submit_booking_request(self) -> None:
        self.client.force_login(self.user)
        start = timezone.now() + timedelta(days=1)
        end = start + timedelta(hours=2)
        response = self.client.post(
            reverse("venue-detail", kwargs={"slug": self.venue.slug}),
            {
                "start_datetime": start.strftime("%Y-%m-%dT%H:%M"),
                "end_datetime": end.strftime("%Y-%m-%dT%H:%M"),
                "notes": "Looking forward to the event.",
                "addons": [str(self.addon.pk)],
            },
        )
        self.assertRedirects(response, reverse("booked-places"))
        booking = Booking.objects.get(user=self.user, venue=self.venue)
        self.assertEqual(booking.status, Booking.STATUS_PENDING)
        self.assertTrue(booking.addons.filter(pk=self.addon.pk).exists())
        self.assertTrue(hasattr(booking, "payment"))
        self.assertEqual(booking.payment.total_amount, booking.total_cost)

    def test_booking_requires_distinct_times(self) -> None:
        self.client.force_login(self.user)
        start = timezone.now() + timedelta(days=2)
        response = self.client.post(
            reverse("venue-detail", kwargs={"slug": self.venue.slug}),
            {
                "start_datetime": start.strftime("%Y-%m-%dT%H:%M"),
                "end_datetime": start.strftime("%Y-%m-%dT%H:%M"),
            },
            follow=True,
        )
        self.assertRedirects(
            response, reverse("venue-detail", kwargs={"slug": self.venue.slug})
        )
        self.assertEqual(Booking.objects.count(), 0)
        messages = list(response.context["messages"])
        self.assertTrue(any("Unable to create booking" in str(message) for message in messages))
