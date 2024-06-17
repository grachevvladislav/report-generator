from core.filters import DateFilter
from django.contrib import admin
from django.db.models import Sum
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path
from utils import add_messages

from .forms import TrainerCsvForm
from .models import Accrual, Contract, Rule, SalaryCertificate, Sale
from .serializers import AccrualSerializer, SaleSerializer


class ActivitieTypeAdmin(admin.ModelAdmin):
    """ActivitieType admin site."""

    list_display = (
        "full_name",
        "duration_in_hours",
        "salary",
    )
    search_fields = ("full_name",)
    list_filter = ("salary",)


class SalaryCertificateAdmin(admin.ModelAdmin):
    """SalaryCertificate model admin site."""

    fields = [
        "number",
        ("start_date", "end_date"),
    ]


class RuleAdmin(admin.ModelAdmin):
    """Rule model admin site."""

    fields = [
        "type",
        "name",
        "rate_value",
        "required_fields",
        "percentage_value",
    ]


class RuleInLine(admin.TabularInline):
    """Inline add Rule for Contract edit."""

    model = Rule
    extra = 0
    # fields = ['type', 'name']


class ContractAdmin(admin.ModelAdmin):
    """ContractAdmin model admin site."""

    list_display = ["number", "employee", "role", "is_active"]
    inlines = [
        RuleInLine,
    ]


class AccrualAdmin(admin.ModelAdmin):
    """Accrual model admin site."""

    list_display = ("date", "employee", "name", "base", "sum")
    list_filter = (DateFilter,)

    change_list_template = "change_list.html"
    change_form_template = "admin/change_form.html"

    def import_csv(self, request):
        """Add schedule button."""
        context = {
            **self.admin_site.each_context(request),
            "title": "Загрузка файла отчета о проведенных занятиях",
            "opts": self.model._meta,
            "form": TrainerCsvForm(),
        }
        if request.method == "POST":
            form = TrainerCsvForm(request.POST, request.FILES)
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
                "import_accrual_csv/",
                self.import_csv,
                name="import_accrual_csv",
            ),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        """Add import csv button."""
        extra_context = extra_context or {}
        extra_context["buttons"] = [
            {"url": "admin:import_accrual_csv", "name": "Загрузить CSV"},
        ]
        response = super().changelist_view(request, extra_context)
        try:
            qs = response.context_data["cl"].queryset
            total = qs.aggregate(Sum("sum"))["sum__sum"]
        except (AttributeError, KeyError):
            pass
        else:
            response.context_data["total"] = total
        return response


class SaleAdmin(admin.ModelAdmin):
    """Sale model admin site."""

    list_display = ("date", "employee", "name", "sum")
    list_filter = (DateFilter,)

    change_list_template = "change_list.html"
    change_form_template = "admin/change_form.html"

    def import_csv(self, request):
        """Add schedule button."""
        context = {
            **self.admin_site.each_context(request),
            "title": "Загрузка файла отчета о продажах",
            "opts": self.model._meta,
            "form": TrainerCsvForm(),
        }
        if request.method == "POST":
            form = TrainerCsvForm(request.POST, request.FILES)
            if "db_save" in request.POST:
                data = request.session.get("uploaded_data", [])
                serializer = SaleSerializer(data=data, many=True)
                if serializer.is_valid():
                    serializer.save()
                    return redirect("admin:salary_accrual_changelist")
                else:
                    add_messages(
                        request,
                        [str(er) for er in serializer.errors],
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
                "import_sale_csv/",
                self.import_csv,
                name="import_sale_csv",
            ),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        """Add import csv button."""
        extra_context = extra_context or {}
        extra_context["buttons"] = [
            {"url": "admin:import_sale_csv", "name": "Загрузить CSV"},
        ]
        response = super().changelist_view(request, extra_context)
        try:
            qs = response.context_data["cl"].queryset
            total = qs.aggregate(Sum("sum"))["sum__sum"]
        except (AttributeError, KeyError):
            pass
        else:
            response.context_data["total"] = total
        return response


admin.site.register(SalaryCertificate, SalaryCertificateAdmin)
admin.site.register(Accrual, AccrualAdmin)
admin.site.register(Sale, SaleAdmin)
admin.site.register(Rule, RuleAdmin)
admin.site.register(Contract, ContractAdmin)