from django.contrib import admin
from .models import Tag, TagType, MainTag, SubTag
from django.http import HttpResponse
from import_export.admin import ImportExportModelAdmin

# Register your models here.


class MainTagAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ["id", "tag_name", "tag_type"]

    list_display_links = ["tag_name"]

    ordering = ["tag_name"]

    list_filter = ["tag_type__tag_type"]

    search_fields = []


class SubTagAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ["id", "tag_name", "tag_type"]

    list_display_links = ["tag_name"]

    ordering = ["tag_name"]

    list_filter = ["tag_type__tag_type"]

    search_fields = []


class TagAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ["id", "tag_name", "parent", "child", "tag_type"]

    list_display_links = ["id", "tag_name"]

    ordering = ["parent__tag_name", "child__tag_name"]

    list_filter = ["parent", "child", "tag_type"]

    search_fields = ["parent", "child"]


class TagTypeAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ["id", "tag_type"]

    list_display_links = ["tag_type"]

    ordering = ["id"]


admin.site.register(MainTag, MainTagAdmin)
admin.site.register(SubTag, SubTagAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(TagType, TagTypeAdmin)
