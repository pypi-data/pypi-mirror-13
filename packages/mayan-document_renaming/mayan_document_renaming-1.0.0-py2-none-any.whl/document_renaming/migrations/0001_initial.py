# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0028_newversionblock'),
    ]

    operations = [
        migrations.CreateModel(
            name='RenamingTemplate',
            fields=[
                (
                    'id', models.AutoField(
                        verbose_name='ID', serialize=False, auto_created=True,
                        primary_key=True
                    )
                ),
                (
                    'template', models.TextField(verbose_name='Template')
                ),
                (
                    'document_type', models.OneToOneField(
                        related_name='rename_template',
                        verbose_name='Document type',
                        to='documents.DocumentType'
                    )
                ),
            ],
            options={
                'verbose_name': 'Renaming template',
                'verbose_name_plural': 'Renaming templates',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Sequence',
            fields=[
                (
                    'id', models.AutoField(
                        verbose_name='ID', serialize=False, auto_created=True,
                        primary_key=True
                    )
                ),
                (
                    'label', models.CharField(
                        unique=True, max_length=32, verbose_name='Label'
                    )
                ),
                ('slug', models.SlugField(verbose_name='Slug')),
                ('value', models.IntegerField(verbose_name='Value')),
            ],
            options={
                'verbose_name': 'Sequence',
                'verbose_name_plural': 'Sequences',
            },
            bases=(models.Model,),
        ),
    ]
