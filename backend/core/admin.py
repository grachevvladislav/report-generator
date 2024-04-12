from datetime import datetime

from admin_extra_buttons.mixins import ExtraButtonsMixin
from django.contrib import admin, messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path

from .crud import export_all_tables, get_missing_dates
from .filters import DateFilter, EmployeeScheduleFiler
from .models import (
    ActivitieType,
    BotRequest,
    Default,
    Document,
    Employee,
    Schedule,
)
from .utils import plural_days


class EmployeeAdmin(admin.ModelAdmin):
    """Employee admin site."""

    list_display = (
        "full_name",
        "tax_regime",
        "is_active",
        "role",
    )
    search_fields = ("tax_regime",)
    list_filter = ("is_active", "role")


class BotRequestAdmin(admin.ModelAdmin):
    """BotRequest admin site."""

    list_display = (
        "full_name",
        "username",
        "telegram_id",
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Only administrators can be on the schedule."""
        if db_field.name == "employee":
            kwargs["queryset"] = Employee.objects.filter(
                is_active=True,
                telegram_id__isnull=True,
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class ActivitieTypeAdmin(admin.ModelAdmin):
    """ActivitieType admin site."""

    list_display = (
        "full_name",
        "duration_in_hours",
        "salary",
    )
    search_fields = ("full_name",)
    list_filter = ("salary",)


class DefaultAdmin(ExtraButtonsMixin, admin.ModelAdmin):
    """DefaultAdmin admin site."""

    list_display = (
        "work_time",
        "planning_horizon",
    )

    change_list_template = "change_list.html"
    change_form_template = "admin/change_form.html"

    def make_backup(self, request):
        """Download backup file function."""
        messages.success(request, "Загрузка начата!")
        file = export_all_tables()
        response = HttpResponse(file, content_type="application/json")
        response["Content-Disposition"] = (
            "attachment; filename=data_"
            + datetime.today().strftime("%d.%m.%Y_%H:%M:%S")
            + ".json"
        )
        return response

    def get_urls(self):
        """Add backup endpoint."""
        urls = super().get_urls()
        custom_urls = [
            path("make_backup/", self.make_backup, name="make_backup"),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        """Add backup button."""
        extra_context = extra_context or {}
        extra_context["buttons"] = [
            {"url": "admin:make_backup", "name": "Сделать бекап"},
        ]
        return super().changelist_view(request, extra_context=extra_context)


class DocumentAdmin(admin.ModelAdmin):
    """Document model admin site."""

    fields = [
        "number",
        ("start_date", "end_date"),
    ]


class ScheduleAdmin(ExtraButtonsMixin, admin.ModelAdmin):
    """ScheduleAdmin admin site."""

    actions = ("set_default_time",)
    list_editable = ("employee",)
    ordering = ("-date",)
    list_filter = (DateFilter, EmployeeScheduleFiler)
    list_display = ("date", "employee", "time")

    change_list_template = "change_list.html"
    change_form_template = "admin/change_form.html"

    async def insert_schedule(self, request):
        """Add schedule button."""
        if request.method == "POST":
            Schedule.objects.abulk_create(
                [
                    Schedule(date=date)
                    for date in get_missing_dates(enable_empty=False)
                ]
            )
            messages.success(request, "Записи добавлены!")
            return redirect("admin:core_schedule_changelist")
        else:
            context = {
                **self.admin_site.each_context(request),
                "title": "Вставить расписание",
                "text": f"Добавить недостающие записи на {plural_days(await Default.get_default('planning_horizon'))}?",
                "title2": "Создаваемые записи",
                "objects": get_missing_dates(enable_empty=False),
                "opts": self.model._meta,
            }
            return TemplateResponse(request, "confirm.html", context)

    def get_urls(self):
        """Add insert_schedule endpoint."""
        urls = super().get_urls()
        custom_urls = [
            path(
                "insert_schedule/",
                self.insert_schedule,
                name="insert_schedule",
            ),
        ]
        return custom_urls + urls

    async def achangelist_view(self, request, extra_context=None):
        """Add notice of deficiencies in next 30 day's planning."""
        difference = await get_missing_dates(enable_empty=True)
        if difference:
            grouped_dates = []
            current_group = [difference[0]]
            for i in range(1, len(difference)):
                if (difference[i] - difference[i - 1]).days == 1:
                    current_group.append(difference[i])
                else:
                    grouped_dates.append(current_group)
                    current_group = [difference[i]]
            grouped_dates.append(current_group)
            msg_storage = messages.get_messages(request)
            msg_list = [m.message for m in msg_storage]
            for group in grouped_dates:
                if len(group) == 1:
                    text = f"Не назначен сотрудник на {group[0].strftime('%d %B')}"
                else:
                    text = f"Не назначен сотрудник c {group[0].strftime('%d %B')} по {group[-1].strftime('%d %B')}"
                if text not in msg_list:
                    messages.error(request, text)
            msg_storage.used = False
        extra_context = extra_context or {}
        extra_context["buttons"] = [
            {"url": "admin:insert_schedule", "name": "Вставить расписание"},
        ]
        return super().changelist_view(request, extra_context=extra_context)

    @admin.action(description="Установить рабочее время по умолчанию")
    async def set_default_time(self, request, queryset):
        """Set worktime from defaults."""
        work_time = await Default.get_default("work_time")
        if not work_time:
            messages.error(request, "Время по умолчанию не указано!")
        else:
            for obj in queryset:
                obj.time = work_time
                obj.save()
            messages.success(request, "Успех!")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Only administrators can be on the schedule."""
        if db_field.name == "employee":
            kwargs["queryset"] = Employee.objects.filter(
                role__in=[Employee.Role.ADMIN, Employee.Role.OWNER],
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(ActivitieType, ActivitieTypeAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Default, DefaultAdmin)
admin.site.register(Schedule, ScheduleAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(BotRequest, BotRequestAdmin)
