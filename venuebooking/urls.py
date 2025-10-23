"""Root URL configuration for the venue booking project."""
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include("venues.auth_urls")),
    path("", include("venues.urls")),
    path("favicon.ico", RedirectView.as_view(url="/static/images/favicon.ico")),
]
