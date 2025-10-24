from __future__ import annotations
from django import forms
from .models import Review


def _rating_choices() -> list[tuple[str, str]]:
    """Return the rating choices used by the review form."""

    return [
        (str(value), f"{value} Star{'s' if value != 1 else ''}")
        for value in range(1, 6)
    ]


class ReviewForm(forms.ModelForm):
    """Form that captures a venue review."""

    rating = forms.TypedChoiceField(
        choices=_rating_choices(),
        coerce=int,
        initial=5,
        label="Rating",
        error_messages={
            "required": "Please select a rating between 1 and 5.",
        },
    )

    comment = forms.CharField(
        label="Comment",
        widget=forms.Textarea(
            attrs={
                "class": "w-full rounded-2xl border border-white/20 bg-white/10 px-4 py-4 text-white placeholder-white/60 backdrop-blur",
                "rows": 4,
            }
        ),
    )

    class Meta:
        model = Review
        fields = ("rating", "comment")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        rating_widget = forms.RadioSelect(attrs={"class": "review-rating-control__radio-list"})
        rating_widget.choices = self.fields["rating"].choices
        self.fields["rating"].widget = rating_widget
        self.fields["comment"].widget.attrs.setdefault(
            "placeholder", "Share what made your experience memorable..."
        )