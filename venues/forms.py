"""Form definitions for the venue booking application."""
from __future__ import annotations

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Booking, Payment, Review


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "w-full rounded-xl bg-white/10 border border-white/30 px-4 py-3 text-white placeholder-white/60 backdrop-blur",
            "placeholder": "Username",
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "w-full rounded-xl bg-white/10 border border-white/30 px-4 py-3 text-white placeholder-white/60 backdrop-blur",
            "placeholder": "Password",
        })
    )


class RegistrationForm(UserCreationForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full rounded-xl bg-white/10 border border-white/30 px-4 py-3 text-white placeholder-white/60 backdrop-blur",
                "placeholder": "Password",
            }
        ),
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full rounded-xl bg-white/10 border border-white/30 px-4 py-3 text-white placeholder-white/60 backdrop-blur",
                "placeholder": "Confirm Password",
            }
        ),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username",)
        widgets = {
            "username": forms.TextInput(
                attrs={
                    "class": "w-full rounded-xl bg-white/10 border border-white/30 px-4 py-3 text-white placeholder-white/60 backdrop-blur",
                    "placeholder": "Username",
                }
            )
        }


class BookingForm(forms.ModelForm):
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


class PaymentForm(forms.ModelForm):
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


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ("rating", "comment")
        widgets = {
            "rating": forms.NumberInput(
                attrs={
                    "min": 1,
                    "max": 5,
                    "class": "w-full rounded-xl border border-white/40 bg-white/10 px-4 py-3 text-white backdrop-blur",
                }
            ),
            "comment": forms.Textarea(
                attrs={
                    "class": "w-full rounded-xl border border-white/40 bg-white/10 px-4 py-3 text-white placeholder-white/60 backdrop-blur",
                    "rows": 4,
                }
            ),
        }


class SearchFilterForm(forms.Form):
    city = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "rounded-xl border border-white/20 bg-white/10 px-4 py-3 text-sm text-white placeholder-white/60 backdrop-blur",
                "placeholder": "City",
            }
        ),
    )
    category = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "rounded-xl border border-white/20 bg-white/10 px-4 py-3 text-sm text-white placeholder-white/60 backdrop-blur",
                "placeholder": "Category",
            }
        ),
    )
    max_price = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(
            attrs={
                "class": "rounded-xl border border-white/20 bg-white/10 px-4 py-3 text-sm text-white placeholder-white/60 backdrop-blur",
                "placeholder": "Max Price",
            }
        ),
    )
