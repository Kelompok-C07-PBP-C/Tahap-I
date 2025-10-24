"""Seed the database with demo content."""
from __future__ import annotations

from datetime import datetime, time, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from ...models import (
    AddOn,
    Booking,
    Category,
    Payment,
    Review,
    Venue,
    VenueAvailability,
    Wishlist,
)


CATEGORY_ADDONS: dict[str, list[tuple[str, str, Decimal]]] = {
    "futsal": [
        (
            "Premium lighting",
            "Enhanced lighting package for night matches",
            Decimal("50000"),
        ),
        (
            "Match futsal balls",
            "Set of 4 FIFA-quality futsal balls for crisp passing.",
            Decimal("75000"),
        ),
        (
            "Goalkeeper kit rental",
            "Protective gloves and pads for one goalkeeper.",
            Decimal("65000"),
        ),
    ],
    "basketball": [
        (
            "Premium lighting",
            "Enhanced lighting package for televised-quality games.",
            Decimal("65000"),
        ),
        (
            "Scoreboard operator",
            "Dedicated staff to run the digital scoreboard.",
            Decimal("85000"),
        ),
        (
            "Basketball bundle",
            "Six indoor composite leather basketballs ready for play.",
            Decimal("60000"),
        ),
    ],
    "badminton": [
        (
            "LED court lighting",
            "Shadow-free LED lighting tuned for shuttle visibility.",
            Decimal("40000"),
        ),
        (
            "Feather shuttlecocks",
            "Tube of 12 tournament grade feather shuttlecocks.",
            Decimal("55000"),
        ),
        (
            "Racket restring service",
            "On-site restringing for up to two rackets during your session.",
            Decimal("90000"),
        ),
    ],
}

DEFAULT_ADDONS: list[tuple[str, str, Decimal]] = [
    (
        "Premium lighting",
        "Enhanced lighting package for night matches",
        Decimal("50000"),
    ),
    (
        "Professional referee",
        "Certified referee service for competitive games",
        Decimal("150000"),
    ),
]


class Command(BaseCommand):
    help = "Populate the database with demo venues, users, and bookings."

    def handle(self, *args, **options):
        with transaction.atomic():
            self.stdout.write("Resetting demo data...")
            self._create_admin()
            user = self._create_demo_user()
            venues = self._create_catalog()
            self._create_bookings(user, venues)
        self.stdout.write(self.style.SUCCESS("Demo data ready. You can log in with 'demo' / 'Demo123!'"))

    def _create_admin(self):
        user_model = get_user_model()
        if not user_model.objects.filter(is_staff=True).exists():
            admin = user_model.objects.create_user(
                "admin", password="Admin123!", is_staff=True, is_superuser=True
            )
            self.stdout.write(self.style.SUCCESS("Created default admin account: admin / Admin123!"))
        else:
            self.stdout.write("Admin account already present. Skipping creation.")

    def _create_demo_user(self):
        user_model = get_user_model()
        user, created = user_model.objects.get_or_create(username="demo")
        if created:
            user.set_password("Demo123!")
            user.save()
            self.stdout.write(self.style.SUCCESS("Created demo user: demo / Demo123!"))
        return user

    def _create_catalog(self) -> list[Venue]:
        categories = {
            "futsal": "Futsal Arenas",
            "basketball": "Basketball Courts",
            "badminton": "Badminton Halls",
        }
        category_objs = {}
        for slug, name in categories.items():
            category, _ = Category.objects.get_or_create(slug=slug, defaults={"name": name})
            category_objs[slug] = category

        venue_specs = [
            {
                "name": "Skyline Futsal Dome",
                "category": category_objs["futsal"],
                "description": "Premium futsal court with climate control, smart lighting, and professional-grade turf.",
                "location": "Central Jakarta",
                "city": "Jakarta",
                "address": "Jl. Merdeka No. 123, Jakarta",
                "price_per_hour": Decimal("350000"),
                "capacity": 12,
                "facilities": "Locker room,Shower,Lounge,Parking",
                "image_url": "https://images.unsplash.com/photo-1517649763962-0c623066013b?auto=format&fit=crop&w=800&q=80",
            },
            {
                "name": "Aurora Hoops Pavilion",
                "category": category_objs["basketball"],
                "description": "Glass-roofed basketball court with viewing gallery and digital scoreboard.",
                "location": "Bandung",
                "city": "Bandung",
                "address": "Jl. Braga No. 88, Bandung",
                "price_per_hour": Decimal("420000"),
                "capacity": 20,
                "facilities": "Changing rooms,Café,Parking,Equipment rental",
                "image_url": "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=800&q=80",
            },
            {
                "name": "Featherlite Badminton Hub",
                "category": category_objs["badminton"],
                "description": "Tournament-ready badminton complex with cushioned floors and LED panel lighting.",
                "location": "Yogyakarta",
                "city": "Yogyakarta",
                "address": "Jl. Malioboro No. 17, Yogyakarta",
                "price_per_hour": Decimal("250000"),
                "capacity": 8,
                "facilities": "Locker room,Equipment store,Cafeteria,Wi-Fi",
                "image_url": "https://images.unsplash.com/photo-1601288496920-b6154fe362d7?auto=format&fit=crop&w=800&q=80",
            },
        ]

        created_venues: list[Venue] = []
        for spec in venue_specs:
            venue, _ = Venue.objects.update_or_create(
                slug=slugify(spec["name"]),
                defaults=spec,
            )
            created_venues.append(venue)
            self._ensure_addons(venue)
            self._ensure_availability(venue)
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(created_venues)} venues."))
        return created_venues

    def _ensure_addons(self, venue: Venue):
        category_slug = getattr(venue.category, "slug", "") or ""
        addons = CATEGORY_ADDONS.get(category_slug, DEFAULT_ADDONS)
        keep_names = [name for name, *_ in addons]

        # Remove stale add-ons that are no longer part of the curated list.
        venue.addons.exclude(name__in=keep_names).delete()

        for name, description, price in addons:
            AddOn.objects.update_or_create(
                venue=venue,
                name=name,
                defaults={"description": description, "price": price},
            )

    def _ensure_availability(self, venue: Venue):
        VenueAvailability.objects.filter(venue=venue).delete()
        base = timezone.now().replace(hour=9, minute=0, second=0, microsecond=0)
        for day_offset in range(3):
            start = base + timedelta(days=day_offset)
            end = start + timedelta(hours=3)
            VenueAvailability.objects.create(venue=venue, start_datetime=start, end_datetime=end)

    def _create_bookings(self, user, venues: list[Venue]):
        if not venues:
            return
        base_date = timezone.localdate() + timedelta(days=1)
        start = timezone.make_aware(datetime.combine(base_date, time(hour=9)))
        end = start + timedelta(hours=2)
        booking, created = Booking.objects.get_or_create(
            user=user,
            venue=venues[0],
            start_datetime=start,
            end_datetime=end,
            defaults={"notes": "Friendly scrimmage with the neighbourhood team."},
        )
        if not created:
            booking.notes = "Friendly scrimmage with the neighbourhood team."
            booking.save(update_fields=["notes", "updated_at"])
        booking.addons.set(list(booking.venue.addons.all()[:1]))
        Payment.objects.update_or_create(
            booking=booking,
            defaults={
                "method": "qris",
                "status": "confirmed",
                "total_amount": booking.total_cost,
                "deposit_amount": Decimal("10000"),
                "reference_code": "VS-DEMO-0001",
            },
        )
        Review.objects.update_or_create(
            user=user,
            venue=booking.venue,
            defaults={
                "rating": 5,
                "comment": "Fantastic facility with spotless amenities and friendly staff!",
            },
        )
        Wishlist.objects.get_or_create(user=user, venue=booking.venue)
        self.stdout.write(self.style.SUCCESS("Sample booking, payment, and review are ready."))
