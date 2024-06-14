from django.contrib import admin
from .models import Tag, TagType
from django.http import HttpResponse
from import_export.admin import ImportExportModelAdmin

# Register your models here.


class TagAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ["id", "tag_name", "parent", "tag_type"]

    list_display_links = ["tag_name"]

    ordering = ["parent", "tag_name"]

    list_filter = ["parent", "tag_type"]

    search_fields = ["tag_name"]


class TagTypeAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ["id", "tag_type"]

    list_display_links = ["tag_type"]

    ordering = ["id"]


admin.site.register(Tag, TagAdmin)
admin.site.register(TagType, TagTypeAdmin)
