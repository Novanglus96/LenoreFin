from django.contrib import admin
from .models import ErrorLevel, Option, LogEntry, Message, Payee
from django.http import HttpResponse
from import_export.admin import ImportExportModelAdmin

# Register your models here.


class LogAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = [
        "log_date",
        "error_level",
        "error_num",
        "log_entry",
        "account",
        "reminder",
        "transaction",
    ]

    list_filter = ["error_level", "error_num"]

    ordering = ["-log_date"]


admin.site.register(ErrorLevel)
admin.site.register(Option)
admin.site.register(LogEntry, LogAdmin)
admin.site.register(Payee)
admin.site.register(Message)
