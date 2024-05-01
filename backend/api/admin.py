from django.contrib import admin
from .models import (
    Account,
    AccountType,
    Tag,
    ChristmasGift,
    ContribRule,
    Contribution,
    ErrorLevel,
    TransactionType,
    Repeat,
    Reminder,
    Note,
    Option,
    TransactionStatus,
    Transaction,
    TransactionDetail,
    LogEntry,
    Payee,
    TagType,
    Bank,
    Message,
    Paycheck,
    FileImport,
    TransactionImport,
    TransactionImportTag,
    TransactionImportError,
    TypeMapping,
    StatusMapping,
    AccountMapping,
    TagMapping,
    TransactionImage,
)
from django.http import HttpResponse


class TransactionDetailInline(admin.TabularInline):
    model = TransactionDetail
    extra = 1


class TransactionAdmin(admin.ModelAdmin):
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

    list_filter = ["source_account_id"]

    ordering = ["-sort_order"]

    inlines = [TransactionDetailInline]


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

    list_filter = ["error_level", "error_num"]

    ordering = ["-log_date"]


# Register your models here.

admin.site.register(Account)
admin.site.register(AccountType)
admin.site.register(Tag)
admin.site.register(ChristmasGift)
admin.site.register(ContribRule)
admin.site.register(Contribution)
admin.site.register(ErrorLevel)
admin.site.register(TransactionType)
admin.site.register(Repeat)
admin.site.register(Reminder)
admin.site.register(Note)
admin.site.register(Option)
admin.site.register(TransactionStatus)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(TransactionDetail)
admin.site.register(LogEntry, LogAdmin)
admin.site.register(Payee)
admin.site.register(TagType)
admin.site.register(Bank)
admin.site.register(Message)
admin.site.register(Paycheck)
admin.site.register(TransactionImage)


@admin.register(
    FileImport,
    TransactionImport,
    TransactionImportTag,
    TransactionImportError,
    TypeMapping,
    StatusMapping,
    AccountMapping,
    TagMapping,
)
class ImportAdmin(admin.ModelAdmin):
    pass
