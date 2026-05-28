from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import ReportConfig, ReportConfigTag, ReportResult


class ReportConfigTagInline(TabularInline):
    model = ReportConfigTag
    extra = 0


class ReportResultInline(TabularInline):
    model = ReportResult
    extra = 0
    readonly_fields = ["run_at", "status", "error_message"]
    fields = ["run_at", "status", "error_message"]
    can_delete = False


@admin.register(ReportConfig)
class ReportConfigAdmin(ModelAdmin):
    list_display = ["name", "report_type", "date_range_type", "group_by", "is_scheduled", "schedule_frequency", "schedule_day", "next_run_at", "created_by", "updated_at"]
    list_filter = ["report_type", "group_by", "date_range_type", "is_scheduled", "schedule_frequency"]
    search_fields = ["name", "description"]
    inlines = [ReportConfigTagInline, ReportResultInline]


@admin.register(ReportResult)
class ReportResultAdmin(ModelAdmin):
    list_display = ["config", "run_at", "status"]
    list_filter = ["status"]
    readonly_fields = ["config", "run_at", "status", "error_message", "result_data"]
