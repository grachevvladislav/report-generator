from django.contrib import admin, messages
from django.template.response import TemplateResponse
from django.urls import path

from .forms import CsvForm
from .models import Accrual, ActivitieType, Document


class ActivitieTypeAdmin(admin.ModelAdmin):
    """ActivitieType admin site."""

    list_display = (
        "full_name",
        "duration_in_hours",
        "salary",
    )
    search_fields = ("full_name",)
    list_filter = ("salary",)


class DocumentAdmin(admin.ModelAdmin):
    """Document model admin site."""

    fields = [
        "number",
        ("start_date", "end_date"),
    ]


class AccrualAdmin(admin.ModelAdmin):
    """Accrual model admin site."""

    list_display = ("date", "employee", "name", "base", "sum")

    change_list_template = "change_list.html"
    change_form_template = "admin/change_form.html"

    def import_csv(self, request):
        """Add schedule button."""
        context = {
            **self.admin_site.each_context(request),
            "title": "Загрузка файла отчета о проведенных занятиях",
            "opts": self.model._meta,
            "submit_csv_form": CsvForm,
        }
        if request.method == "POST":
            form = CsvForm(request.POST)
            if form.is_valid():
                pass
            else:
                context["is_load"] = True
                print(form.errors.items())
                messages.error(request, str(""))
                return TemplateResponse(request, "load_file.html", context)
        else:
            context["is_load"] = False
            return TemplateResponse(request, "load_file.html", context)

    def get_urls(self):
        """Add import_csv endpoint."""
        urls = super().get_urls()
        custom_urls = [
            path(
                "import_csv/",
                self.import_csv,
                name="import_csv",
            ),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        """Add import csv button."""
        extra_context = extra_context or {}
        extra_context["buttons"] = [
            {"url": "admin:import_csv", "name": "Загрузить CSV"},
        ]
        return super().changelist_view(request, extra_context=extra_context)


admin.site.register(ActivitieType, ActivitieTypeAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(Accrual, AccrualAdmin)
