from django.contrib import admin
from .models import AccountType, Bank, Account
from django.http import HttpResponse
from import_export.admin import ImportExportModelAdmin

# Register your models here.

admin.site.register(AccountType)
admin.site.register(Account)
admin.site.register(Bank)
