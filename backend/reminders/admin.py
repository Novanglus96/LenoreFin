from django.contrib import admin
from .models import Reminder, Repeat
from django.http import HttpResponse
from import_export.admin import ImportExportModelAdmin

# Register your models here.

admin.site.register(Repeat)
admin.site.register(Reminder)
