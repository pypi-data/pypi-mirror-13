from __future__ import unicode_literals

from django.contrib import admin

from .models import RenamingTemplate, Sequence


@admin.register(RenamingTemplate)
class RenamingTemplateAdmin(admin.ModelAdmin):
    list_display = ('document_type',)


@admin.register(Sequence)
class SequenceAdmin(admin.ModelAdmin):
    list_display = ('label', 'slug', 'increment', 'value')
    list_display_links = ('label', 'slug',)
