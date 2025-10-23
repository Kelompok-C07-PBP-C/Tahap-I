from django.apps import AppConfig


class VenuesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "venues"
    verbose_name = "Venue Booking"

    def ready(self):  # pragma: no cover - used for signals
        from . import signals  # noqa: F401
