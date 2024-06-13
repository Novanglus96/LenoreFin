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

admin.site.register(FileImport)
admin.site.register(TransactionImport)
admin.site.register(TransactionImportTag)
admin.site.register(TransactionImportError)
admin.site.register(TypeMapping)
admin.site.register(StatusMapping)
admin.site.register(AccountMapping)
admin.site.register(TagMapping)
