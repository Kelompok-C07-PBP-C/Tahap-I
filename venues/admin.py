"""Admin registrations for the venue booking app."""
from __future__ import annotations

from django.contrib import admin

from .models import AddOn, Booking, Category, Payment, Review, Venue, VenueAvailability, Wishlist


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    prepopulated_fields = {"slug": ("name",)}


class AddOnInline(admin.TabularInline):
    model = AddOn
    extra = 1


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "price_per_hour", "category")
    list_filter = ("city", "category")
    search_fields = ("name", "city")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [AddOnInline]


@admin.register(VenueAvailability)
class VenueAvailabilityAdmin(admin.ModelAdmin):
    list_display = ("venue", "start_datetime", "end_datetime")
    list_filter = ("venue",)


class BookingPaymentInline(admin.StackedInline):
    model = Payment
    can_delete = False
    extra = 0


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("venue", "user", "start_datetime", "end_datetime")
    list_filter = ("venue", "user")
    search_fields = ("venue__name", "user__username")
    inlines = [BookingPaymentInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("booking", "method", "status", "total_amount", "updated_at")
    list_filter = ("status", "method")
    search_fields = ("reference_code",)


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("user", "venue", "created_at")
    list_filter = ("user",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("venue", "user", "rating", "created_at")
    list_filter = ("rating", "venue")
    search_fields = ("comment", "venue__name", "user__username")
