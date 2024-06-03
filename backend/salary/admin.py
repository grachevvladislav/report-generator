from core.filters import DateFilter
from django.contrib import admin
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path
from utils import add_messages

from .filters import EmployeeAccrualFilter
from .forms import CsvForm
from .models import Accrual, ActivitieType, Document
from .serializers import AccrualSerializer


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
    list_filter = (DateFilter, EmployeeAccrualFilter)

    change_list_template = "change_list.html"
    change_form_template = "admin/change_form.html"

    def import_csv(self, request):
        """Add schedule button."""
        context = {
            **self.admin_site.each_context(request),
            "title": "Загрузка файла отчета о проведенных занятиях",
            "opts": self.model._meta,
            "form": CsvForm(),
        }
        if request.method == "POST":
            form = CsvForm(request.POST, request.FILES)
            if "db_save" in request.POST:
                data = request.session.get("uploaded_data", [])
                serializer = AccrualSerializer(data=data, many=True)
                if serializer.is_valid():
                    serializer.save()
                    return redirect("admin:salary_accrual_changelist")
                else:
                    add_messages(
                        request,
                        [
                            str(er["non_field_errors"][0])
                            for er in serializer.errors
                        ],
                    )
            elif form.is_valid():
                request.session["uploaded_data"] = AccrualSerializer(
                    form.cleaned_data["csv_file"], many=True
                ).data
                context["objects"] = form.cleaned_data["csv_file"]
            else:
                err = form.errors["csv_file"].as_text()
                fix_err = err.replace("* [&#x27;", "").replace("&#x27;]", "")
                add_messages(request, fix_err.split("&#x27;, &#x27;"))
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
