from django.contrib import admin
from core.admin import UnfoldImportExportModelAdmin
from .models import Tag, TagType, MainTag, SubTag


class MainTagAdmin(UnfoldImportExportModelAdmin):
    list_display = ["id", "tag_name", "tag_type", "is_system", "slug"]
    list_display_links = ["tag_name"]
    ordering = ["tag_name"]
    list_filter = ["tag_type__tag_type"]
    readonly_fields = ["slug"]
    search_fields = []

    def has_delete_permission(self, request, obj=None):
        if obj is not None and obj.is_system:
            return False
        return super().has_delete_permission(request, obj)

    def delete_queryset(self, request, queryset):
        queryset.filter(is_system=False).delete()


class SubTagAdmin(UnfoldImportExportModelAdmin):
    list_display = ["id", "tag_name", "tag_type", "is_system", "slug"]
    list_display_links = ["tag_name"]
    ordering = ["tag_name"]
    list_filter = ["tag_type__tag_type"]
    readonly_fields = ["slug"]
    search_fields = []

    def has_delete_permission(self, request, obj=None):
        if obj is not None and obj.is_system:
            return False
        return super().has_delete_permission(request, obj)

    def delete_queryset(self, request, queryset):
        queryset.filter(is_system=False).delete()


class TagAdmin(UnfoldImportExportModelAdmin):
    list_display = ["id", "tag_name", "parent", "child", "tag_type", "is_system", "slug"]
    list_display_links = ["id", "tag_name"]
    ordering = ["parent__tag_name", "child__tag_name"]
    list_filter = ["parent", "child", "tag_type"]
    readonly_fields = ["slug"]
    search_fields = ["parent", "child"]

    def has_delete_permission(self, request, obj=None):
        if obj is not None and obj.is_system:
            return False
        return super().has_delete_permission(request, obj)

    def delete_queryset(self, request, queryset):
        queryset.filter(is_system=False).delete()


class TagTypeAdmin(UnfoldImportExportModelAdmin):
    list_display = ["id", "tag_type", "is_system", "slug"]
    list_display_links = ["tag_type"]
    ordering = ["id"]
    readonly_fields = ["slug"]

    def has_delete_permission(self, request, obj=None):
        if obj is not None and obj.is_system:
            return False
        return super().has_delete_permission(request, obj)

    def delete_queryset(self, request, queryset):
        queryset.filter(is_system=False).delete()


admin.site.register(MainTag, MainTagAdmin)
admin.site.register(SubTag, SubTagAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(TagType, TagTypeAdmin)
