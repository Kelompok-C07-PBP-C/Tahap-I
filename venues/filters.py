"""Filter definitions for catalogue views."""
from __future__ import annotations

from django import forms
import django_filters

from .models import Category, Venue


class VenueFilter(django_filters.FilterSet):
    city = django_filters.ChoiceFilter(
        field_name="city",
        lookup_expr="exact",
        empty_label="All cities",
        widget=forms.Select(
            attrs={
                "class": "custom-select w-full rounded-xl border border-white/20 bg-white/10 px-4 py-3 text-sm text-white backdrop-blur",
            }
        ),
    )
    category = django_filters.ModelChoiceFilter(
        field_name="category",
        queryset=Category.objects.all(),
        empty_label="All categories",
        widget=forms.Select(
            attrs={
                "class": "custom-select w-full rounded-xl border border-white/20 bg-white/10 px-4 py-3 text-sm text-white backdrop-blur",
            }
        ),
    )
    max_price = django_filters.NumberFilter(
        field_name="price_per_hour",
        lookup_expr="lte",
        widget=forms.NumberInput(
            attrs={
                "class": "w-full rounded-xl border border-white/20 bg-white/10 px-4 py-3 text-sm text-white placeholder-white/60 backdrop-blur",
                "placeholder": "Max Price",
                "min": 0,
                "step": "0.01",
            }
        ),
    )

    class Meta:
        model = Venue
        fields = ["city", "category", "max_price"]

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        if queryset is None:
            queryset = Venue.objects.all()
        super().__init__(data=data, queryset=queryset, request=request, prefix=prefix)

        city_values = (
            self.queryset.order_by("city")
            .values_list("city", flat=True)
            .distinct()
        )
        city_choices = [("", "All cities")] + [
            (value, value) for value in city_values if value
        ]

        if "city" in self.filters:
            self.filters["city"].field.choices = city_choices
        if "city" in self.form.fields:
            self.form.fields["city"].choices = city_choices
