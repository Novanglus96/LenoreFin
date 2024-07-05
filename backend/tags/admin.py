from django.contrib import admin
from .models import Tag, TagType, MainTag, SubTag
from django.http import HttpResponse
from import_export.admin import ImportExportModelAdmin

# Register your models here.


class MainTagAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = []

    list_display_links = []

    ordering = []

    list_filter = []

    search_fields = []


class SubTagAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = []

    list_display_links = []

    ordering = []

    list_filter = []

    search_fields = []


class TagAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ["id", "parent", "child", "tag_type"]

    list_display_links = ["id"]

    ordering = ["parent", "child"]

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
