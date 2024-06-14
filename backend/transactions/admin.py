from django.contrib import admin
from .models import (
    ErrorLevel,
    TransactionType,
    Option,
    TransactionStatus,
    Transaction,
    TransactionDetail,
    LogEntry,
    Payee,
    Message,
    Paycheck,
    TransactionImage,
)
from django.http import HttpResponse
from import_export.admin import ImportExportModelAdmin


class TransactionDetailInline(admin.TabularInline):
    model = TransactionDetail
    extra = 1


class TransactionAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = [
        "id",
        "sort_order",
        "transaction_date",
        "status",
        "checkNumber",
        "total_amount",
        "description",
        "transaction_type",
        "running_total",
        "edit_date",
        "add_date",
        "memo",
        "reminder",
        "paycheck",
        "account_id",
        "source_account_id",
        "destination_account_id",
        "related_transaction",
    ]

    search_fields = ["id"]

    list_filter = ["source_account_id"]

    ordering = ["-sort_order"]

    inlines = [TransactionDetailInline]


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


# Register your models here.

admin.site.register(ErrorLevel)
admin.site.register(TransactionType)
admin.site.register(Option)
admin.site.register(TransactionStatus)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(TransactionDetail)
admin.site.register(LogEntry, LogAdmin)
admin.site.register(Payee)
admin.site.register(Message)
admin.site.register(Paycheck)
admin.site.register(TransactionImage)
