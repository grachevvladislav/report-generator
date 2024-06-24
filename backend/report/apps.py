from django.apps import AppConfig


class ReportConfig(AppConfig):
    """App config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "report"
    verbose_name = "Загрузка отчётов"
