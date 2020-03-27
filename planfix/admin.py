from __future__ import unicode_literals

from django.contrib import admin
from .models import PlanfixModel


@admin.register(PlanfixModel)
class PlanfixModelAdmin(admin.ModelAdmin):
    list_display = ['contact_id', 'task_id', 'user']
    list_display_links = ('user',)
