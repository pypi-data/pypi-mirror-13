# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mezzanine_references', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='reference',
            name='subtitle',
            field=models.CharField(max_length=32, null=True, verbose_name='Subtitle', blank=True),
        ),
    ]
