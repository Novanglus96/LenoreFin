from django.contrib import admin
from unfold.admin import ModelAdmin
from core.admin import UnfoldImportExportModelAdmin
from .models import (
    ChristmasGift,
    WindfallRule,
    Bucket,
    Note,
    CalculationRule,
    Budget,
    DetectedRecurring,
    PlanAcceptance,
    WindfallApplication,
)


class ChristmasGiftAdmin(UnfoldImportExportModelAdmin):
    list_display = ["id", "budget", "tag"]
    list_display_links = ["id", "tag"]
    ordering = ["tag"]


class WindfallRuleAdmin(UnfoldImportExportModelAdmin):
    list_display = ["id", "order", "rule", "bucket", "cap", "cap_amount"]
    list_display_links = ["id", "rule"]
    ordering = ["order", "id"]


class BucketAdmin(UnfoldImportExportModelAdmin):
    list_display = ["id", "name", "contribution_per_paycheck", "goal_amount", "goal_date", "account", "reminder", "active"]
    list_display_links = ["name"]
    ordering = ["name"]


class PlanAcceptanceAdmin(ModelAdmin):
    list_display = ["id", "accepted_on", "window_start", "window_end", "total_per_paycheck", "reverted_on"]
    ordering = ["-accepted_on"]


class WindfallApplicationAdmin(ModelAdmin):
    list_display = ["id", "arrival_date", "amount", "allocated", "source_account", "reverted_on"]
    ordering = ["-arrival_date"]


class NoteAdmin(UnfoldImportExportModelAdmin):
    list_display = ["id", "note_date", "note_text"]
    list_display_links = ["note_date"]
    ordering = ["-note_date", "-id"]


class CalculationRuleAdmin(UnfoldImportExportModelAdmin):
    list_display = ["id", "name"]
    list_display_links = ["name"]
    ordering = ["id"]


class BudgetAdmin(UnfoldImportExportModelAdmin):
    list_display = ["id", "name", "amount", "start_day"]
    list_display_links = ["name"]
    ordering = ["name"]


class DetectedRecurringAdmin(ModelAdmin):
    list_display = ["description", "estimated_amount", "repeat", "next_estimated_date", "is_ignored", "created_at"]
    list_filter = ["is_ignored"]
    search_fields = ["description"]


admin.site.register(ChristmasGift, ChristmasGiftAdmin)
admin.site.register(WindfallRule, WindfallRuleAdmin)
admin.site.register(Bucket, BucketAdmin)
admin.site.register(PlanAcceptance, PlanAcceptanceAdmin)
admin.site.register(WindfallApplication, WindfallApplicationAdmin)
admin.site.register(Note, NoteAdmin)
admin.site.register(CalculationRule, CalculationRuleAdmin)
admin.site.register(Budget, BudgetAdmin)
admin.site.register(DetectedRecurring, DetectedRecurringAdmin)
