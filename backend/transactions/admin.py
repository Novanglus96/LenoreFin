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


class TransactionImageInLine(admin.TabularInline):
    model = TransactionImage
    extra = 1


class TransactionTypeAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ["id", "transaction_type"]

    list_display_links = ["transaction_type"]

    ordering = ["id"]


class TransactionStatusAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ["id", "transaction_status"]

    list_display_links = ["transaction_status"]

    ordering = ["id"]


class TransactionAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = [
        "id",
        "transaction_date",
        "status",
        "checkNumber",
        "total_amount",
        "description",
        "transaction_type",
        "edit_date",
        "add_date",
        "memo",
        "paycheck",
        "source_account",
        "destination_account",
    ]

    search_fields = ["id"]

    list_filter = ["source_account", "destination_account"]

    ordering = []

    inlines = [TransactionDetailInline, TransactionImageInLine]


class PaycheckAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = [
        "id",
        "payee",
        "gross",
        "net",
        "taxes",
        "health",
        "pension",
        "fsa",
        "dca",
        "union_dues",
        "four_fifty_seven_b",
    ]

    list_display_links = ["id", "payee"]

    search_fields = ["payee", "gross", "net"]

    ordering = ["id"]

    list_filter = ["payee"]


# Register your models here.

admin.site.register(TransactionType, TransactionTypeAdmin)
admin.site.register(TransactionStatus, TransactionStatusAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Paycheck, PaycheckAdmin)
