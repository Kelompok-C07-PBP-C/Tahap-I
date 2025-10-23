"""View package exports."""
from __future__ import annotations

from .admin import (
    AdminDashboardView,
    AdminVenueCreateView,
    AdminVenueDeleteView,
    AdminVenueListView,
    AdminVenueUpdateView,
)
from .auth import AuthLoginView, AuthLogoutView, RegisterView
from .booking import BookingPaymentView
from .catalog import CatalogView, catalog_filter
from .detail import VenueDetailView
from .home import HomeView
from .wishlist import WishlistToggleView, WishlistView, wishlist_toggle

__all__ = [
    "AdminDashboardView",
    "AdminVenueCreateView",
    "AdminVenueDeleteView",
    "AdminVenueListView",
    "AdminVenueUpdateView",
    "AuthLoginView",
    "AuthLogoutView",
    "RegisterView",
    "BookingPaymentView",
    "CatalogView",
    "catalog_filter",
    "VenueDetailView",
    "HomeView",
    "WishlistToggleView",
    "WishlistView",
    "wishlist_toggle",
]
