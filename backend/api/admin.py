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
admin.site.register(Transaction)
admin.site.register(TransactionDetail)
admin.site.register(LogEntry)
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
