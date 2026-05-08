from django.contrib import admin
from .models import (
    TransactionType,
    TransactionStatus,
    Transaction,
    TransactionDetail,
    Paycheck,
    TransactionImage,
    ReminderCacheTransaction,
    ForecastCacheTransaction,
    ReminderCacheTransactionDetail,
    ForecastCacheTransactionDetail,
)
from import_export.admin import ImportExportModelAdmin


class TransactionDetailInline(admin.TabularInline):
    model = TransactionDetail
    extra = 1


class TransactionImageInLine(admin.TabularInline):
    model = TransactionImage
    extra = 1


class ReminderCacheTransactionDetailInline(admin.TabularInline):
    model = ReminderCacheTransactionDetail
    extra = 1


class ForecastCacheTransactionDetailInline(admin.TabularInline):
    model = ForecastCacheTransactionDetail
    extra = 1


class TransactionDetailAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ["id", "transaction", "tag", "detail_amt"]

    list_display_links = ["id"]

    ordering = ["-transaction__transaction_date"]

    search_fields = ["detail_amt"]

    list_filter = ["tag"]


class ReminderCacheTransactionDetailAdmin(
    ImportExportModelAdmin, admin.ModelAdmin
):
    list_display = ["id", "transaction", "tag", "detail_amt"]

    list_display_links = ["id"]

    ordering = ["-transaction__transaction_date"]

    search_fields = ["detail_amt"]

    list_filter = ["tag"]


class ForecastCacheTransactionDetailAdmin(
    ImportExportModelAdmin, admin.ModelAdmin
):
    list_display = ["id", "transaction", "tag", "detail_amt"]

    list_display_links = ["id"]

    ordering = ["-transaction__transaction_date"]

    search_fields = ["detail_amt"]

    list_filter = ["tag"]


class TransactionTypeAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ["id", "transaction_type", "is_system", "slug"]

    list_display_links = ["transaction_type"]

    ordering = ["id"]

    def has_delete_permission(self, request, obj=None):
        if obj is not None and obj.is_system:
            return False
        return super().has_delete_permission(request, obj)

    def delete_queryset(self, request, queryset):
        queryset.filter(is_system=False).delete()


class TransactionStatusAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ["id", "transaction_status", "is_system", "slug"]

    list_display_links = ["transaction_status"]

    ordering = ["id"]

    def has_delete_permission(self, request, obj=None):
        if obj is not None and obj.is_system:
            return False
        return super().has_delete_permission(request, obj)

    def delete_queryset(self, request, queryset):
        queryset.filter(is_system=False).delete()


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


class ReminderCacheTransactionAdmin(ImportExportModelAdmin, admin.ModelAdmin):
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
        "reminder",
    ]

    search_fields = ["id"]

    list_filter = ["source_account", "destination_account"]

    ordering = []

    inlines = [
        ReminderCacheTransactionDetailInline,
    ]


class ForecastCacheTransactionAdmin(ImportExportModelAdmin, admin.ModelAdmin):
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

    inlines = [
        ForecastCacheTransactionDetailInline,
    ]


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
admin.site.register(TransactionDetail, TransactionDetailAdmin)
admin.site.register(ReminderCacheTransaction, ReminderCacheTransactionAdmin)
admin.site.register(ForecastCacheTransaction, ForecastCacheTransactionAdmin)
admin.site.register(
    ForecastCacheTransactionDetail,
    ForecastCacheTransactionDetailAdmin,
)
admin.site.register(
    ReminderCacheTransactionDetail,
    ReminderCacheTransactionDetailAdmin,
)
