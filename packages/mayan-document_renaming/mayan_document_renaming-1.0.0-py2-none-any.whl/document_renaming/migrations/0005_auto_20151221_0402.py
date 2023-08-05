# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('document_renaming', '0004_auto_20151220_0751'),
    ]

    operations = [
        migrations.AlterField(
            model_name='renamingtemplate',
            name='template',
            field=models.TextField(
                help_text='Sequences are available as '
                '"sequence_[sequence slug]". To obtain the next value for a '
                'sequence, call it\'s next_value method, ie: '
                '"invoice-{{ sequence_invoices.next_value }}.',
                verbose_name='Template', blank=True
            ),
            preserve_default=True,
        ),
    ]
