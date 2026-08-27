from django.contrib import admin
from unfold.admin import ModelAdmin
from core.admin import UnfoldImportExportModelAdmin
from .models import ChristmasGift, ContribRule, Contribution, Note, CalculationRule, Budget, DetectedRecurring


class ChristmasGiftAdmin(UnfoldImportExportModelAdmin):
    list_display = ["id", "budget", "tag"]
    list_display_links = ["id", "tag"]
    ordering = ["tag"]


class ContribRuleAdmin(UnfoldImportExportModelAdmin):
    list_display = ["id", "rule", "cap"]
    list_display_links = ["id", "rule"]
    ordering = ["id"]


class ContributionAdmin(UnfoldImportExportModelAdmin):
    list_display = ["id", "contribution", "priority", "per_paycheck", "minimum_per_paycheck", "target_balance", "sweep", "active"]
    list_display_links = ["contribution"]
    ordering = ["id"]


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
admin.site.register(ContribRule, ContribRuleAdmin)
admin.site.register(Contribution, ContributionAdmin)
admin.site.register(Note, NoteAdmin)
admin.site.register(CalculationRule, CalculationRuleAdmin)
admin.site.register(Budget, BudgetAdmin)
admin.site.register(DetectedRecurring, DetectedRecurringAdmin)
