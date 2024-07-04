from django.contrib import admin

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

    fields = [
        "number",
        "contract",
        ("start_date", "end_date"),
        "date_of_creation",
        "original_signed",
    ]
    list_display = (
        "number",
        "contract",
        "original_signed",
    )
    list_filter = (SalaryCertificateDateFilter,)


class ContractAdmin(admin.ModelAdmin):
    """Contract model admin site."""

    list_display = ["display_name", "template", "is_active"]
    list_filter = ["template"]


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

    list_display = ["name", "is_active"]

    inlines = [
        AmountOfAccrualInLine,
        RateInLine,
        PercentageOfSalesInLine,
        HourlyPaymentInLine,
    ]

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
