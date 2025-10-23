"""View package exports.

The legacy ``views.py`` shim has been deleted so Django imports this
package directly; keeping explicit exports here preserves backwards
compatibility for modules that still import ``venues.views``.
"""
from __future__ import annotations

from .admin import (
    AdminDashboardView,
    AdminBookingApprovalView,
    AdminVenueCreateView,
    AdminVenueDeleteView,
    AdminVenueListView,
    AdminVenueUpdateView,
)
from .auth import AuthLoginView, AuthLogoutView, RegisterView
from .booking import BookedPlacesView, BookingCancelView, BookingPaymentView
from .catalog import CatalogView, catalog_filter
from .detail import VenueDetailView
from .home import HomeView
from .wishlist import WishlistToggleView, WishlistView, wishlist_toggle

__all__ = [
    "AdminDashboardView",
    "AdminBookingApprovalView",
    "AdminVenueCreateView",
    "AdminVenueDeleteView",
    "AdminVenueListView",
    "AdminVenueUpdateView",
    "AuthLoginView",
    "AuthLogoutView",
    "RegisterView",
    "BookedPlacesView",
    "BookingPaymentView",
    "BookingCancelView",
    "CatalogView",
    "catalog_filter",
    "VenueDetailView",
    "HomeView",
    "WishlistToggleView",
    "WishlistView",
    "wishlist_toggle",
]
