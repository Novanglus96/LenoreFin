from django.contrib import admin
from .models import Reminder, Repeat, ReminderExclusion
from import_export.admin import ImportExportModelAdmin


# Register your models here.


class ReminderExclusionAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ["id", "reminder", "exclude_date"]

    list_display_links = ["id", "reminder"]

    ordering = ["reminder", "exclude_date"]


class RepeatAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ["id", "repeat_name", "days", "weeks", "months", "years", "is_system", "slug"]

    list_display_links = ["repeat_name"]

    ordering = ["id"]

    readonly_fields = ["slug"]

    def has_delete_permission(self, request, obj=None):
        if obj is not None and obj.is_system:
            return False
        return super().has_delete_permission(request, obj)

    def delete_queryset(self, request, queryset):
        queryset.filter(is_system=False).delete()


class ReminderAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = [
        "id",
        "description",
        "amount",
        "next_date",
        "start_date",
        "end_date",
        "auto_add",
    ]

    list_display_links = ["id", "description"]

    ordering = ["next_date", "description", "id"]


admin.site.register(Repeat, RepeatAdmin)
admin.site.register(Reminder, ReminderAdmin)
admin.site.register(ReminderExclusion, ReminderExclusionAdmin)
