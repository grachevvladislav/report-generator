import datetime

from core.models import Employee
from django.contrib import admin, messages
from django.db.utils import IntegrityError
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path
from utils import last_day_of_the_previous_month

from constants import months

from .crud import create_documents_for_last_month, create_pdf
from .filters import SalaryCertificateDateFilter
from .models import (
    AmountOfAccrual,
    Contract,
    ContractTemplate,
    HourlyPayment,
    PercentageOfSales,
    Rate,
    SalaryCertificate,
)


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

    actions = ("download_document",)
    fields = (
        "number",
        "contract",
        ("start_date", "end_date"),
        "date_of_creation",
        "original_signed",
    )
    list_display = ("admin_name", "contract", "admin_sum")
    list_filter = (
        SalaryCertificateDateFilter,
        "contract__template",
        "original_signed",
    )
    ordering = ("-number",)

    change_list_template = "change_list.html"
    change_form_template = "admin/change_form.html"

    def create_multiple(self, request):
        """Add certificate."""
        if request.method == "POST":
            try:
                # need to add objects from context
                SalaryCertificate.objects.bulk_create(
                    create_documents_for_last_month()
                )
            except IntegrityError as e:
                messages.error(request, e)
            else:
                messages.success(request, "Записи добавлены!")
            return redirect("admin:salary_salarycertificate_changelist")
        else:
            context = {
                **self.admin_site.each_context(request),
                "title": "Создать акты за прошлый месяц",
                "title2": f"Создаваемые записи за {months[last_day_of_the_previous_month().month - 1].lower()}",
                "objects": create_documents_for_last_month(),
                "opts": self.model._meta,
            }
            return TemplateResponse(request, "confirm.html", context)

    def changelist_view(self, request, extra_context=None):
        """Add custom button."""
        extra_context = extra_context or {}
        extra_context["buttons"] = [
            {
                "url": "admin:create_multiple",
                "name": "Создать акты за прошлый месяц",
            },
        ]
        return super().changelist_view(request, extra_context=extra_context)

    def get_urls(self):
        """Add insert_schedule endpoint."""
        urls = super().get_urls()
        custom_urls = [
            path(
                "create_multiple/",
                self.create_multiple,
                name="create_multiple",
            ),
        ]
        return custom_urls + urls

    @admin.action(description="Скачать документ")
    def download_document(self, request, queryset):
        """Download document."""
        file = create_pdf(queryset)
        file_name = datetime.datetime.today().strftime("%d.%m.%Y %H:%M")
        response = HttpResponse(file.read(), content_type="application/x-pdf")
        response[
            "Content-Disposition"
        ] = f'attachment\x3B filename="{file_name}.pdf"'
        return response


class ContractAdmin(admin.ModelAdmin):
    """Contract model admin site."""

    list_display = (
        "admin_name",
        "template",
        "original_signed",
        "is_active",
    )
    list_filter = ("template", "original_signed")
    ordering = ("-number",)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Only administrators can be on the schedule."""
        if db_field.name == "employee":
            kwargs["queryset"] = Employee.objects.all().order_by("surname")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class RateInLine(admin.TabularInline):
    """Inline add Rate rule for ContractTemplate edit."""

    model = Rate
    extra = 0


class AmountOfAccrualInLine(admin.TabularInline):
    """Inline add AmountOfAccrual rule for ContractTemplate edit."""

    model = AmountOfAccrual
    extra = 0


class PercentageOfSalesInLine(admin.TabularInline):
    """Inline add PercentageOfSales rule for ContractTemplate edit."""

    model = PercentageOfSales
    extra = 0


class HourlyPaymentInLine(admin.TabularInline):
    """Inline add HourlyPayment rule for ContractTemplate edit."""

    model = HourlyPayment
    extra = 0


class ContractTemplateAdmin(admin.ModelAdmin):
    """ContractTemplate model admin site."""

    list_display = ("name", "is_active")

    inlines = (
        AmountOfAccrualInLine,
        RateInLine,
        PercentageOfSalesInLine,
        HourlyPaymentInLine,
    )

    def save_model(self, request, obj, form, change):
        """Save bytes to the database."""
        if form.is_valid() and form.cleaned_data["file"]:
            uploaded_img = form.save(commit=False)
            uploaded_img.file_data = form.cleaned_data["file"].file.read()
            uploaded_img.save()
        super().save_model(request, obj, form, change)


admin.site.register(SalaryCertificate, SalaryCertificateAdmin)
admin.site.register(Contract, ContractAdmin)
admin.site.register(ContractTemplate, ContractTemplateAdmin)
