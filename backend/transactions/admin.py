from django.contrib import admin
from .models import (
    TransactionType,
    TransactionStatus,
    Transaction,
    TransactionDetail,
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


# Register your models here.

admin.site.register(TransactionType)
admin.site.register(TransactionStatus)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(TransactionDetail)
admin.site.register(Paycheck)
admin.site.register(TransactionImage)
