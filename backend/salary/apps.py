from django.apps import AppConfig


class SalaryConfig(AppConfig):
    """App config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "salary"
    verbose_name = "Зарплата"
