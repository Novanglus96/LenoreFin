from django.contrib import admin
from .models import ReportConfig, ReportConfigTag


class ReportConfigTagInline(admin.TabularInline):
    model = ReportConfigTag
    extra = 0


@admin.register(ReportConfig)
class ReportConfigAdmin(admin.ModelAdmin):
    list_display = ["name", "report_type", "date_range_type", "group_by", "created_by", "updated_at"]
    list_filter = ["report_type", "group_by", "date_range_type"]
    search_fields = ["name", "description"]
    inlines = [ReportConfigTagInline]
