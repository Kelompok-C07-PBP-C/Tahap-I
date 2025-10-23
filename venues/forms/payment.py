"""Payment related forms."""
from __future__ import annotations

from django import forms

from ..models import Payment


class PaymentForm(forms.ModelForm):
    """Form used to confirm payment method."""

    class Meta:
        model = Payment
        fields = ("method",)
        widgets = {
            "method": forms.RadioSelect(
                attrs={
                    "class": "flex flex-col gap-3 text-white",
                }
            )
        }
