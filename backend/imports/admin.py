from django.contrib import admin
from .models import (
    FileImport,
    TransactionImport,
    TransactionImportTag,
    TransactionImportError,
    TypeMapping,
    StatusMapping,
    AccountMapping,
    TagMapping,
)

# Register your models here.


class FileImportAdmin(admin.ModelAdmin):
    list_display = ["id", "import_file", "processed", "successful", "errors"]

    list_display_links = ["id"]

    ordering = ["-id"]

    def has_add_permission(self, request):
        # Return False to disable adding
        return False


class TransactionImportAdmin(admin.ModelAdmin):
    list_display = [
        "file_import",
        "line_id",
        "transaction_date",
        "transaction_type_id",
        "transaction_status_id",
        "amount",
        "description",
        "source_account_id",
        "destination_account_id",
        "memo",
    ]

    list_display_links = ["line_id"]

    ordering = ["-file_import", "line_id"]

    list_filter = ["file_import"]

    search_fields = ["line_id", "amount", "description", "memo"]

    def has_add_permission(self, request):
        # Return False to disable adding
        return False

    def has_change_permission(self, request, obj=None):
        # Return False to disable editing
        return False


class TransactionImportTagAdmin(admin.ModelAdmin):
    list_display = ["transaction_import", "tag_id", "tag_name", "tag_amount"]

    list_display_links = ["tag_id"]

    ordering = ["-transaction_import", "tag_id"]

    def has_add_permission(self, request):
        # Return False to disable adding
        return False

    def has_delete_permission(self, request, obj=None):
        # Return False to disable deleting
        return False

    def has_change_permission(self, request, obj=None):
        # Return False to disable editing
        return False


class TransactionImportErrorAdmin(admin.ModelAdmin):
    list_display = ["id", "transaction_import", "text", "status"]

    list_display_links = ["id", "text"]

    ordering = ["-transaction_import", "id"]

    def has_add_permission(self, request):
        # Return False to disable adding
        return False

    def has_delete_permission(self, request, obj=None):
        # Return False to disable deleting
        return False

    def has_change_permission(self, request, obj=None):
        # Return False to disable editing
        return False


class TypeMappingAdmin(admin.ModelAdmin):
    list_display = ["file_import", "file_type", "type_id"]

    list_display_links = ["file_type"]

    ordering = ["-file_import", "file_type"]

    def has_add_permission(self, request):
        # Return False to disable adding
        return False


class StatusMappingAdmin(admin.ModelAdmin):
    list_display = ["file_import", "file_status", "status_id"]

    list_display_links = ["file_status"]

    ordering = ["-file_import", "file_status"]

    def has_add_permission(self, request):
        # Return False to disable adding
        return False


class AccountMappingAdmin(admin.ModelAdmin):
    list_display = ["file_import", "file_account", "account_id"]

    list_display_links = ["file_account"]

    ordering = ["-file_import", "file_account"]

    def has_add_permission(self, request):
        # Return False to disable adding
        return False


class TagMappingAdmin(admin.ModelAdmin):
    list_display = ["file_import", "file_tag", "tag_id"]

    list_display_links = ["file_tag"]

    ordering = ["-file_import", "file_tag"]

    def has_add_permission(self, request):
        # Return False to disable adding
        return False


admin.site.register(FileImport, FileImportAdmin)
admin.site.register(TransactionImport, TransactionImportAdmin)
admin.site.register(TransactionImportTag, TransactionImportTagAdmin)
admin.site.register(TransactionImportError, TransactionImportErrorAdmin)
admin.site.register(TypeMapping, TypeMappingAdmin)
admin.site.register(StatusMapping, StatusMappingAdmin)
admin.site.register(AccountMapping, AccountMappingAdmin)
admin.site.register(TagMapping, TagMappingAdmin)
