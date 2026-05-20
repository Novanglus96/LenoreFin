from django.contrib import admin
from unfold.admin import ModelAdmin
from import_export.admin import ImportExportModelAdmin
from .models import ChristmasGift, ContribRule, Contribution, Note, CalculationRule, Budget


class ChristmasGiftAdmin(ModelAdmin, ImportExportModelAdmin):
    list_display = ["id", "budget", "tag"]
    list_display_links = ["id", "tag"]
    ordering = ["tag"]


class ContribRuleAdmin(ModelAdmin, ImportExportModelAdmin):
    list_display = ["id", "rule", "cap"]
    list_display_links = ["id", "rule"]
    ordering = ["id"]


class ContributionAdmin(ModelAdmin, ImportExportModelAdmin):
    list_display = ["id", "contribution", "per_paycheck", "emergency_amt", "emergency_diff", "cap", "active"]
    list_display_links = ["contribution"]
    ordering = ["id"]


class NoteAdmin(ModelAdmin, ImportExportModelAdmin):
    list_display = ["id", "note_date", "note_text"]
    list_display_links = ["note_date"]
    ordering = ["-note_date", "-id"]


class CalculationRuleAdmin(ModelAdmin, ImportExportModelAdmin):
    list_display = ["id", "name"]
    list_display_links = ["name"]
    ordering = ["id"]


class BudgetAdmin(ModelAdmin, ImportExportModelAdmin):
    list_display = ["id", "name", "amount", "start_day"]
    list_display_links = ["name"]
    ordering = ["name"]


admin.site.register(ChristmasGift, ChristmasGiftAdmin)
admin.site.register(ContribRule, ContribRuleAdmin)
admin.site.register(Contribution, ContributionAdmin)
admin.site.register(Note, NoteAdmin)
admin.site.register(CalculationRule, CalculationRuleAdmin)
admin.site.register(Budget, BudgetAdmin)
