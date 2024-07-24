from django.contrib import admin
from .models import ErrorLevel, Option, LogEntry, Message, Payee
from django.http import HttpResponse
from import_export.admin import ImportExportModelAdmin

# Register your models here.


class LogAdmin(admin.ModelAdmin):
    list_display = [
        "log_date",
        "error_level",
        "error_num",
        "log_entry",
        "account",
        "reminder",
        "transaction",
    ]

    list_display_links = [
        "log_date",
        "log_entry",
    ]

    list_filter = ["error_level", "error_num"]

    ordering = ["-log_date"]

    def has_add_permission(self, request):
        # Return False to disable adding
        return False

    # def has_delete_permission(self, request, obj=None):
    # Return False to disable deleting
    #   return False

    def has_change_permission(self, request, obj=None):
        # Return False to disable editing
        return False


class OptionAdmin(admin.ModelAdmin):

    def has_add_permission(self, request, obj=None):
        # Only allow adding if no instances exist
        return not Option.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Disable delete permission
        return False

    def change_view(self, request, object_id, form_url="", extra_context=None):
        # Redirect to the singleton instance change page
        singleton = Option.load()
        if singleton:
            return super(OptionAdmin, self).change_view(
                request, str(singleton.pk), form_url, extra_context
            )
        else:
            return super(OptionAdmin, self).change_view(
                request, object_id, form_url, extra_context
            )

    list_display = ["log_level", "alert_balance", "alert_period"]

    list_display_links = ["log_level", "alert_balance", "alert_period"]


class ErrorLevelAdmin(admin.ModelAdmin):
    list_display = ["id", "error_level"]

    list_display_links = ["error_level"]

    ordering = ["id"]


class PayeeAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ["id", "payee_name"]

    list_display_links = ["payee_name"]

    ordering = ["payee_name"]


class MessageAdmin(admin.ModelAdmin):
    list_display = ["message_date", "message", "unread"]

    list_display_links = ["message"]

    ordering = ["-message_date"]

    def has_add_permission(self, request):
        # Return False to disable adding
        return False

    def has_delete_permission(self, request, obj=None):
        # Return False to disable deleting
        return False

    def has_change_permission(self, request, obj=None):
        # Return False to disable editing
        return False


admin.site.register(ErrorLevel, ErrorLevelAdmin)
admin.site.register(Option, OptionAdmin)
admin.site.register(LogEntry, LogAdmin)
admin.site.register(Payee, PayeeAdmin)
admin.site.register(Message, MessageAdmin)
