# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('document_renaming', '0002_sequence_increment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sequence',
            name='slug',
            field=models.SlugField(
                help_text='Do not use hypens, if you need spacing use '
                'underscores.', verbose_name='Slug'
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='sequence',
            name='value',
            field=models.IntegerField(default=0, verbose_name='Value'),
            preserve_default=True,
        ),
    ]
