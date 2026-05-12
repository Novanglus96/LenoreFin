from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import (
    GraphType,
    Option,
    Message,
    Payee,
    Version,
    DescriptionHistory,
)
from import_export.admin import ImportExportModelAdmin

# Register your models here.


class OptionAdmin(admin.ModelAdmin):

    def has_add_permission(self, request, obj=None):
        # Only allow adding if no instances exist
        return not Option.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Disable delete permission
        return False

    def change_view(self, request, object_id, form_url="", extra_context=None):
        # Redirect to the singleton instance change page
        singleton = Option.load()
        if singleton:
            return super(OptionAdmin, self).change_view(
                request, str(singleton.pk), form_url, extra_context
            )
        else:
            return super(OptionAdmin, self).change_view(
                request, object_id, form_url, extra_context
            )

    list_display = [
        "alert_balance",
        "alert_period",
        "auto_archive",
        "archive_length",
    ]

    list_display_links = [
        "alert_balance",
        "alert_period",
        "auto_archive",
        "archive_length",
    ]


class PayeeAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ["id", "payee_name"]

    list_display_links = ["payee_name"]

    ordering = ["payee_name"]


class MessageAdmin(admin.ModelAdmin):
    list_display = ["message_date", "message", "unread"]

    list_display_links = ["message"]

    ordering = ["-message_date"]

    def has_add_permission(self, request):
        # Return False to disable adding
        return False

    def has_delete_permission(self, request, obj=None):
        # Return False to disable deleting
        return False

    def has_change_permission(self, request, obj=None):
        # Return False to disable editing
        return False


class VersionAdmin(admin.ModelAdmin):
    list_display = ["version_number"]

    list_display_links = ["version_number"]

    ordering = ["version_number"]

    def has_add_permission(self, request):
        # Return False to disable adding
        return False

    def has_delete_permission(self, request, obj=None):
        # Return False to disable deleting
        return False

    def has_change_permission(self, request, obj=None):
        # Return False to disable editing
        return False


class DescriptionHistoryAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ["id", "description_pretty", "tag"]

    list_display_links = ["description_pretty"]

    ordering = ["id"]


class RestrictedUserAdmin(UserAdmin):
    """
    Readonly-group users can only view and change their own profile.
    Full Access users and superusers retain normal UserAdmin behaviour.
    """

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.groups.filter(name="Full Access").exists():
            return qs
        return qs.filter(pk=request.user.pk)

    def has_add_permission(self, request):
        if request.user.is_superuser or request.user.groups.filter(name="Full Access").exists():
            return super().has_add_permission(request)
        return False

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser or request.user.groups.filter(name="Full Access").exists():
            return super().has_delete_permission(request, obj)
        return False

    def has_change_permission(self, request, obj=None):
        if obj is None:
            return True
        if request.user.is_superuser or request.user.groups.filter(name="Full Access").exists():
            return super().has_change_permission(request, obj)
        return obj.pk == request.user.pk

    def get_readonly_fields(self, request, obj=None):
        readonly = super().get_readonly_fields(request, obj)
        if request.user.is_superuser or request.user.groups.filter(name="Full Access").exists():
            return readonly
        return list(readonly) + ["is_superuser", "is_staff", "groups", "user_permissions"]


class GraphTypeAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ["id", "graph_type", "is_system", "slug"]

    list_display_links = ["graph_type"]

    ordering = ["id"]

    readonly_fields = ["slug"]

    def has_delete_permission(self, request, obj=None):
        if obj is not None and obj.is_system:
            return False
        return super().has_delete_permission(request, obj)

    def delete_queryset(self, request, queryset):
        queryset.filter(is_system=False).delete()


admin.site.unregister(User)
admin.site.register(User, RestrictedUserAdmin)

admin.site.register(GraphType, GraphTypeAdmin)
admin.site.register(Option, OptionAdmin)
admin.site.register(Payee, PayeeAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(Version, VersionAdmin)
admin.site.register(DescriptionHistory, DescriptionHistoryAdmin)
