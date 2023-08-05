# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('document_renaming', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sequence',
            name='increment',
            field=models.IntegerField(default=1, verbose_name='Increment'),
            preserve_default=True,
        ),
    ]
