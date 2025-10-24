from django.apps import AppConfig


class RentConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "rent"
    verbose_name = "Penyewaan Lapangan"

<<<<<<< HEAD
    def ready(self):  # pragma: no cover
        from . import signals  # noqa: F401
=======
    def ready(self):
        from . import signals
>>>>>>> origin/dev
