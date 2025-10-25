"""Inline formset helpers for managing add-ons alongside venues."""
from __future__ import annotations

from typing import Any

from django.forms import BaseInlineFormSet, inlineformset_factory

from manajemen_lapangan.models import Venue

from .forms import AddOnForm
from .models import AddOn


class AddOnInlineFormSet(BaseInlineFormSet):
    """Inline formset that hides the delete checkbox and exposes data hooks."""

    def add_fields(self, form, index):  # type: ignore[override]
        super().add_fields(form, index)
        delete_field = form.fields.get("DELETE")
        if delete_field is not None:
            delete_field.widget.attrs.update(
                {
                    "class": "hidden",
                    "data-addon-delete-input": "true",
                    "style": "display: none;",
                }
            )


def build_addon_formset(*, data: dict[str, Any] | None = None, instance: Venue | None = None) -> BaseInlineFormSet:
    """Return a configured inline formset for editing add-ons.

    Keeping the factory inside the ``add_on`` module helps isolate the logic
    for managing optional equipment while allowing admin views in
    ``manajemen_lapangan`` to reuse the same HTML fragment.
    """

    formset_class = inlineformset_factory(
        Venue,
        AddOn,
        form=AddOnForm,
        extra=3,
        can_delete=True,
        formset=AddOnInlineFormSet,
    )
    return formset_class(data=data or None, instance=instance, prefix="addons")
