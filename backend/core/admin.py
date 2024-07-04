from admin_extra_buttons.mixins import ExtraButtonsMixin
from asgiref.sync import async_to_sync
from django.contrib import admin, messages
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path
from utils import add_messages, plural_days

from .crud import get_missing_dates
from .filters import EmployeeScheduleFilter, ScheduleDateFilter
from .models import BotRequest, Default, Employee, Schedule
from .views import make_backup


class EmployeeAdmin(admin.ModelAdmin):
    """Employee admin site."""

    list_display = ("full_name", "is_active", "force_save")
    search_fields = (
        "tax_regime",
        "is_active",
        "inn",
        "address",
    )
    ordering = ("-is_active", "-force_save", "surname", "name", "patronymic")
    list_filter = ("is_active",)


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


class DefaultAdmin(ExtraButtonsMixin, admin.ModelAdmin):
    """DefaultAdmin admin site."""

    list_display = (
        "work_time",
        "planning_horizon",
        "cashier_telegram_id",
    )

    change_list_template = "change_list.html"
    change_form_template = "admin/change_form.html"

    def get_urls(self):
        """Add backup endpoint."""
        urls = super().get_urls()
        custom_urls = [
            path("make_backup/", make_backup, name="make_backup"),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        """Add backup button."""
        extra_context = extra_context or {}
        extra_context["buttons"] = [
            {"url": "admin:make_backup", "name": "Сделать бекап"},
        ]
        return super().changelist_view(request, extra_context=extra_context)


class ScheduleAdmin(ExtraButtonsMixin, admin.ModelAdmin):
    """ScheduleAdmin admin site."""

    actions = ("set_default_time",)
    list_editable = ("employee",)
    ordering = ("-date",)
    list_filter = (ScheduleDateFilter, EmployeeScheduleFilter)
    list_display = ("full_string", "employee", "time")

    change_list_template = "change_list.html"
    change_form_template = "admin/change_form.html"

    def insert_schedule(self, request):
        """Add schedule button."""
        if request.method == "POST":
            Schedule.objects.bulk_create(
                [
                    Schedule(date=date)
                    for date in async_to_sync(get_missing_dates)(
                        add_empty=True
                    )
                ]
            )
            messages.success(request, "Записи добавлены!")
            return redirect("admin:core_schedule_changelist")
        else:
            context = {
                **self.admin_site.each_context(request),
                "title": "Вставить расписание",
                "text": f"Добавить недостающие записи на {plural_days(Default.get_default('planning_horizon'))}?",
                "title2": "Создаваемые записи",
                "objects": async_to_sync(get_missing_dates)(add_empty=True),
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

    def changelist_view(self, request, extra_context=None):
        """Add notice of deficiencies in next 30 day's planning."""
        difference = async_to_sync(get_missing_dates)(add_empty=False)
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
            msgs = []
            for group in grouped_dates:
                if len(group) == 1:
                    text = f"Не назначен сотрудник на {group[0].strftime('%d %B')}"
                else:
                    text = f"Не назначен сотрудник c {group[0].strftime('%d %B')} по {group[-1].strftime('%d %B')}"
                msgs.append(text)
            add_messages(request, msgs)
        extra_context = extra_context or {}
        extra_context["buttons"] = [
            {"url": "admin:insert_schedule", "name": "Вставить расписание"},
        ]
        return super().changelist_view(request, extra_context=extra_context)

    @admin.action(description="Установить рабочее время по умолчанию")
    def set_default_time(self, request, queryset):
        """Set worktime from defaults."""
        work_time = Default.get_default("work_time")
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
                сontract__template__hourly_payment__isnull=False,
            ).distinct()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Default, DefaultAdmin)
admin.site.register(Schedule, ScheduleAdmin)
admin.site.register(BotRequest, BotRequestAdmin)
