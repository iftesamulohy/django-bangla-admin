from django.apps import AppConfig


class BanglaAdminConfig(AppConfig):
    name = "django_bangla_admin"
    verbose_name = "Bangla Admin"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        # Validate/normalize the BANGLA_ADMIN setting early so misconfiguration
        # surfaces at startup rather than on first request.
        from .conf import ba_conf  # noqa: F401

        ba_conf.reload()
