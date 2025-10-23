"""Reusable search filter form."""
from __future__ import annotations

from django import forms
from django.db import OperationalError, ProgrammingError

from ..models import Category, Venue

from ..models import Category, Venue


class SearchFilterForm(forms.Form):
    """Form displayed in navigation for quick searching."""

    city = forms.ChoiceField(
        required=False,
        choices=(),
        widget=forms.Select(
            attrs={
                "class": "custom-select w-full rounded-xl border border-white/20 bg-white/10 px-4 py-3 text-sm text-white backdrop-blur",
            }
        ),
    )
    category = forms.ModelChoiceField(
        required=False,
        queryset=Category.objects.none(),
        empty_label="All categories",
        widget=forms.Select(
            attrs={
                "class": "custom-select w-full rounded-xl border border-white/20 bg-white/10 px-4 py-3 text-sm text-white backdrop-blur",
            }
        ),
    )
    max_price = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(
            attrs={
                "class": "w-full rounded-xl border border-white/20 bg-white/10 px-4 py-3 text-sm text-white placeholder-white/60 backdrop-blur",
                "placeholder": "Max Price",
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        city_values = (
            Venue.objects.order_by("city")
            .values_list("city", flat=True)
            .distinct()
        )
        self.fields["city"].choices = [("", "All cities")] + [
            (city, city) for city in city_values if city
        ]
        self.fields["category"].queryset = Category.objects.order_by("name")
