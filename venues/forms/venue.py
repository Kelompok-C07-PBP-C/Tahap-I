"""Forms for managing venues and add-ons."""
from __future__ import annotations

from django import forms
from django.utils.text import slugify

from ..models import AddOn, Venue


class VenueForm(forms.ModelForm):
    """Admin form to manage venues."""

    class Meta:
        model = Venue
        fields = (
            "category",
            "name",
            "slug",
            "description",
            "location",
            "city",
            "address",
            "price_per_hour",
            "capacity",
            "facilities",
            "image_url",
            "available_start_time",
            "available_end_time",
        )
        widgets = {
            "category": forms.Select(
                attrs={
                    "class": "w-full rounded-xl border border-white/20 bg-white/10 px-4 py-2 text-white backdrop-blur",
                }
            ),
            "name": forms.TextInput(
                attrs={
                    "class": "w-full rounded-xl border border-white/20 bg-white/10 px-4 py-2 text-white placeholder-white/50 backdrop-blur",
                }
            ),
            "slug": forms.TextInput(
                attrs={
                    "class": "w-full rounded-xl border border-white/20 bg-white/10 px-4 py-2 text-white placeholder-white/50 backdrop-blur",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "w-full rounded-xl border border-white/20 bg-white/10 px-4 py-3 text-white placeholder-white/60 backdrop-blur",
                    "rows": 4,
                }
            ),
            "location": forms.TextInput(
                attrs={
                    "class": "w-full rounded-xl border border-white/20 bg-white/10 px-4 py-2 text-white placeholder-white/50 backdrop-blur",
                }
            ),
            "city": forms.TextInput(
                attrs={
                    "class": "w-full rounded-xl border border-white/20 bg-white/10 px-4 py-2 text-white placeholder-white/50 backdrop-blur",
                }
            ),
            "address": forms.Textarea(
                attrs={
                    "class": "w-full rounded-xl border border-white/20 bg-white/10 px-4 py-3 text-white placeholder-white/60 backdrop-blur",
                    "rows": 3,
                }
            ),
            "price_per_hour": forms.NumberInput(
                attrs={
                    "class": "w-full rounded-xl border border-white/20 bg-white/10 px-4 py-3 text-white placeholder-white/60 backdrop-blur",
                    "step": "0.01",
                }
            ),
            "capacity": forms.NumberInput(
                attrs={
                    "class": "w-full rounded-xl border border-white/20 bg-white/10 px-4 py-3 text-white placeholder-white/60 backdrop-blur",
                    "min": 1,
                }
            ),
            "facilities": forms.Textarea(
                attrs={
                    "class": "w-full rounded-xl border border-white/20 bg-white/10 px-4 py-3 text-white placeholder-white/60 backdrop-blur",
                    "rows": 3,
                }
            ),
            "image_url": forms.TextInput(
                attrs={
                    "class": "w-full rounded-xl border border-white/20 bg-white/10 px-4 py-2 text-white placeholder-white/50 backdrop-blur",
                }
            ),
            "available_start_time": forms.TimeInput(
                attrs={
                    "type": "time",
                    "class": "w-full rounded-xl border border-white/20 bg-white/10 px-4 py-2 text-white placeholder-white/60 backdrop-blur",
                }
            ),
            "available_end_time": forms.TimeInput(
                attrs={
                    "type": "time",
                    "class": "w-full rounded-xl border border-white/20 bg-white/10 px-4 py-2 text-white placeholder-white/60 backdrop-blur",
                }
            ),
        }

    def clean_slug(self):
        slug = self.cleaned_data.get("slug")
        name = self.cleaned_data.get("name")
        base = slug or name
        if base:
            return slugify(base)
        return slug


class AddOnForm(forms.ModelForm):
    """Admin form to manage add-ons."""

    class Meta:
        model = AddOn
        fields = ("name", "description", "price")
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "w-full rounded-xl border border-white/20 bg-white/10 px-4 py-2 text-white placeholder-white/60 backdrop-blur",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "w-full rounded-xl border border-white/20 bg-white/10 px-4 py-3 text-white placeholder-white/60 backdrop-blur",
                    "rows": 2,
                }
            ),
            "price": forms.NumberInput(
                attrs={
                    "class": "w-full rounded-xl border border-white/20 bg-white/10 px-4 py-3 text-white placeholder-white/60 backdrop-blur",
                    "step": "0.01",
                    "min": 0,
                }
            ),
        }
