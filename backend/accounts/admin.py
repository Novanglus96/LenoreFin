from django.contrib import admin
from .models import AccountType, Bank, Account
from django.http import HttpResponse
from import_export.admin import ImportExportModelAdmin

# Register your models here.


class AccountTypeAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ["id", "account_type", "color", "icon"]

    list_display_links = ["account_type"]

    ordering = ["account_type"]


class AccountAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ["id", "account_name", "active", "open_date", "bank"]

    list_display_links = ["account_name"]

    search_fields = ["account_name"]

    ordering = ["account_name"]

    list_filter = ["bank", "active"]


class BankAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ["id", "bank_name"]

    list_display_links = ["bank_name"]

    search_fields = ["bank_name"]

    ordering = ["bank_name"]


admin.site.register(AccountType, AccountTypeAdmin)
admin.site.register(Account, AccountAdmin)
admin.site.register(Bank, BankAdmin)
