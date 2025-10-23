"""Booking related forms."""
from __future__ import annotations

from django import forms

from ..models import Booking


class BookingForm(forms.ModelForm):
    """Form used to capture booking details from the user."""

    start_datetime = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={
                "type": "datetime-local",
                "class": "w-full rounded-xl border border-white/40 bg-white/10 px-4 py-3 text-white placeholder-white/60 backdrop-blur",
            }
        )
    )
    end_datetime = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={
                "type": "datetime-local",
                "class": "w-full rounded-xl border border-white/40 bg-white/10 px-4 py-3 text-white placeholder-white/60 backdrop-blur",
            }
        )
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "w-full rounded-xl border border-white/40 bg-white/10 px-4 py-3 text-white placeholder-white/60 backdrop-blur",
                "rows": 3,
            }
        ),
    )

    class Meta:
        model = Booking
        fields = ("start_datetime", "end_datetime", "notes", "addons")
        widgets = {
            "addons": forms.CheckboxSelectMultiple(
                attrs={
                    "class": "grid grid-cols-1 gap-2 text-white sm:grid-cols-2",
                }
            )
        }
