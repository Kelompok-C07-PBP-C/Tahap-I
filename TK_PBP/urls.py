"""Root URL configuration for TK PBP project."""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

from authentication.views import HomeView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", HomeView.as_view(), name="home"),
    path("", include("authentication.urls")),
    path("workspace/", include("manajemen_lapangan.urls")),
    path("", include("katalog.urls")),
    path("", include("rent.urls")),
    path("", include("interaksi.urls")),
    path("favicon.ico", RedirectView.as_view(url="/static/images/favicon.ico")),
]
