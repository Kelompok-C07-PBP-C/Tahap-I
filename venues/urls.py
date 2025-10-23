"""Application URL patterns."""
from django.urls import path

from . import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("catalog/", views.CatalogView.as_view(), name="catalog"),
    path("wishlist/", views.WishlistView.as_view(), name="wishlist"),
    path("wishlist/<int:pk>/toggle/", views.WishlistToggleView.as_view(), name="wishlist-toggle"),
    path("api/wishlist/<int:pk>/toggle/", views.wishlist_toggle, name="wishlist-toggle-api"),
    path("api/catalog/filter/", views.catalog_filter, name="catalog-filter"),
    path("venue/<slug:slug>/", views.VenueDetailView.as_view(), name="venue-detail"),
    path("booking/<int:pk>/payment/", views.BookingPaymentView.as_view(), name="payment"),
    path("workspace/", views.AdminDashboardView.as_view(), name="admin-dashboard"),
    path("workspace/venues/", views.AdminVenueListView.as_view(), name="admin-venues"),
    path("workspace/venues/add/", views.AdminVenueCreateView.as_view(), name="admin-venue-create"),
    path("workspace/venues/<int:pk>/edit/", views.AdminVenueUpdateView.as_view(), name="admin-venue-edit"),
    path("workspace/venues/<int:pk>/delete/", views.AdminVenueDeleteView.as_view(), name="admin-venue-delete"),
]
