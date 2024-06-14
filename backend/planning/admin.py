from django.contrib import admin
from .models import ChristmasGift, ContribRule, Contribution, Note
from django.http import HttpResponse
from import_export.admin import ImportExportModelAdmin

# Register your models here.

admin.site.register(ChristmasGift)
admin.site.register(ContribRule)
admin.site.register(Contribution)
admin.site.register(Note)
