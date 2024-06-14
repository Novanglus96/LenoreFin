from django.contrib import admin
from .models import Reminder, Repeat
from django.http import HttpResponse
from import_export.admin import ImportExportModelAdmin


# Register your models here.


class RepeatAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ["id", "repeat_name", "days", "weeks", "months", "years"]

    list_display_links = ["repeat_name"]

    ordering = ["id"]


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

    def has_add_permission(self, request):
        # Return False to disable adding
        return False

    def has_delete_permission(self, request, obj=None):
        # Return False to disable deleting
        return False

    def has_change_permission(self, request, obj=None):
        # Return False to disable editing
        return False


admin.site.register(Repeat, RepeatAdmin)
admin.site.register(Reminder, ReminderAdmin)
