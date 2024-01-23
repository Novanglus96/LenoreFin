from django.contrib import admin
from .models import Account, AccountType, CalendarDate, Tag, ChristmasGift, ContribRule, Contribution, ErrorLevel, TransactionType, Repeat, Reminder, Note, Option, TransactionStatus, Transaction, TransactionDetail, LogEntry, Payee, TagType, Bank, Message

# Register your models here.

admin.site.register(Account)
admin.site.register(AccountType)
admin.site.register(CalendarDate)
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
