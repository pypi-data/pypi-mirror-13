# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def initialize_renaming_templates(apps, schema_editor):
    RenamingTemplate = apps.get_model('document_renaming', 'RenamingTemplate')
    DocumentType = apps.get_model('documents', 'DocumentType')

    for document_type in DocumentType.objects.all():
        RenamingTemplate.objects.get_or_create(document_type=document_type)


def destroy_renaming_templates(apps, schema_editor):
    RenamingTemplate = apps.get_model('document_renaming', 'RenamingTemplate')
    RenamingTemplate.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('document_renaming', '0005_auto_20151221_0402'),
    ]

    operations = [
        migrations.RunPython(
            initialize_renaming_templates, destroy_renaming_templates
        ),
    ]
