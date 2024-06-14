from django.contrib import admin
from .models import Tag, TagType
from django.http import HttpResponse
from import_export.admin import ImportExportModelAdmin

# Register your models here.

admin.site.register(Tag)
admin.site.register(TagType)
