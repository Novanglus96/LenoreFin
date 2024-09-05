from django.contrib import admin
from .models import (
    ChristmasGift,
    ContribRule,
    Contribution,
    Note,
    CalculationRule,
)
from django.http import HttpResponse
from import_export.admin import ImportExportModelAdmin

# Register your models here.


class ChristmasGiftAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ["id", "budget", "tag"]

    list_display_links = ["id", "tag"]

    ordering = ["tag"]


class ContribRuleAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ["id", "rule", "cap"]

    list_display_links = ["id", "rule"]

    ordering = ["id"]


class ContributionAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = [
        "id",
        "contribution",
        "per_paycheck",
        "emergency_amt",
        "emergency_diff",
        "cap",
        "active",
    ]

    list_display_links = ["contribution"]

    ordering = ["id"]


class NoteAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ["id", "note_date", "note_text"]

    list_display_links = ["note_date"]

    ordering = ["-note_date", "-id"]


class CalculationRuleAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ["id", "name"]

    list_display_links = ["name"]

    ordering = ["id"]


admin.site.register(ChristmasGift, ChristmasGiftAdmin)
admin.site.register(ContribRule, ContribRuleAdmin)
admin.site.register(Contribution, ContributionAdmin)
admin.site.register(Note, NoteAdmin)
admin.site.register(CalculationRule, CalculationRuleAdmin)
