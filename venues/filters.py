"""Filter definitions for catalogue views."""
from __future__ import annotations

import django_filters

from .models import Venue


class VenueFilter(django_filters.FilterSet):
    city = django_filters.CharFilter(field_name="city", lookup_expr="icontains")
    category = django_filters.CharFilter(field_name="category__name", lookup_expr="icontains")
    max_price = django_filters.NumberFilter(field_name="price_per_hour", lookup_expr="lte")

    class Meta:
        model = Venue
        fields = ["city", "category", "max_price"]
