from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from import_export.admin import ImportExportModelAdmin
from .models import (
    TransactionType, TransactionStatus, Transaction, TransactionDetail,
    Paycheck, TransactionImage, ReminderCacheTransaction, ForecastCacheTransaction,
    ReminderCacheTransactionDetail, ForecastCacheTransactionDetail,
)


class TransactionDetailInline(TabularInline):
    model = TransactionDetail
    extra = 1


class TransactionImageInLine(TabularInline):
    model = TransactionImage
    extra = 1


class ReminderCacheTransactionDetailInline(TabularInline):
    model = ReminderCacheTransactionDetail
    extra = 1


class ForecastCacheTransactionDetailInline(TabularInline):
    model = ForecastCacheTransactionDetail
    extra = 1


class TransactionDetailAdmin(ModelAdmin, ImportExportModelAdmin):
    list_display = ["id", "transaction", "tag", "detail_amt"]
    list_display_links = ["id"]
    ordering = ["-transaction__transaction_date"]
    search_fields = ["detail_amt"]
    list_filter = ["tag"]


class ReminderCacheTransactionDetailAdmin(ModelAdmin, ImportExportModelAdmin):
    list_display = ["id", "transaction", "tag", "detail_amt"]
    list_display_links = ["id"]
    ordering = ["-transaction__transaction_date"]
    search_fields = ["detail_amt"]
    list_filter = ["tag"]


class ForecastCacheTransactionDetailAdmin(ModelAdmin, ImportExportModelAdmin):
    list_display = ["id", "transaction", "tag", "detail_amt"]
    list_display_links = ["id"]
    ordering = ["-transaction__transaction_date"]
    search_fields = ["detail_amt"]
    list_filter = ["tag"]


class TransactionTypeAdmin(ModelAdmin, ImportExportModelAdmin):
    list_display = ["id", "transaction_type", "is_system", "slug"]
    list_display_links = ["transaction_type"]
    ordering = ["id"]
    readonly_fields = ["slug"]

    def has_delete_permission(self, request, obj=None):
        if obj is not None and obj.is_system:
            return False
        return super().has_delete_permission(request, obj)

    def delete_queryset(self, request, queryset):
        queryset.filter(is_system=False).delete()


class TransactionStatusAdmin(ModelAdmin, ImportExportModelAdmin):
    list_display = ["id", "transaction_status", "is_system", "slug"]
    list_display_links = ["transaction_status"]
    ordering = ["id"]
    readonly_fields = ["slug"]

    def has_delete_permission(self, request, obj=None):
        if obj is not None and obj.is_system:
            return False
        return super().has_delete_permission(request, obj)

    def delete_queryset(self, request, queryset):
        queryset.filter(is_system=False).delete()


class TransactionAdmin(ModelAdmin, ImportExportModelAdmin):
    list_display = ["id", "transaction_date", "status", "checkNumber", "total_amount",
                    "description", "transaction_type", "edit_date", "add_date", "memo",
                    "paycheck", "source_account", "destination_account"]
    search_fields = ["id"]
    list_filter = ["source_account", "destination_account"]
    ordering = []
    inlines = [TransactionDetailInline, TransactionImageInLine]


class ReminderCacheTransactionAdmin(ModelAdmin, ImportExportModelAdmin):
    list_display = ["id", "transaction_date", "status", "checkNumber", "total_amount",
                    "description", "transaction_type", "edit_date", "add_date", "memo",
                    "paycheck", "source_account", "destination_account", "reminder"]
    search_fields = ["id"]
    list_filter = ["source_account", "destination_account"]
    ordering = []
    inlines = [ReminderCacheTransactionDetailInline]


class ForecastCacheTransactionAdmin(ModelAdmin, ImportExportModelAdmin):
    list_display = ["id", "transaction_date", "status", "checkNumber", "total_amount",
                    "description", "transaction_type", "edit_date", "add_date", "memo",
                    "paycheck", "source_account", "destination_account"]
    search_fields = ["id"]
    list_filter = ["source_account", "destination_account"]
    ordering = []
    inlines = [ForecastCacheTransactionDetailInline]


class PaycheckAdmin(ModelAdmin, ImportExportModelAdmin):
    list_display = ["id", "payee", "gross", "net", "taxes", "health", "pension",
                    "fsa", "dca", "union_dues", "four_fifty_seven_b"]
    list_display_links = ["id", "payee"]
    search_fields = ["payee", "gross", "net"]
    ordering = ["id"]
    list_filter = ["payee"]


admin.site.register(TransactionType, TransactionTypeAdmin)
admin.site.register(TransactionStatus, TransactionStatusAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Paycheck, PaycheckAdmin)
admin.site.register(TransactionDetail, TransactionDetailAdmin)
admin.site.register(ReminderCacheTransaction, ReminderCacheTransactionAdmin)
admin.site.register(ForecastCacheTransaction, ForecastCacheTransactionAdmin)
admin.site.register(ForecastCacheTransactionDetail, ForecastCacheTransactionDetailAdmin)
admin.site.register(ReminderCacheTransactionDetail, ReminderCacheTransactionDetailAdmin)
