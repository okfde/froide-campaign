# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('froide_campaign', '0004_auto_20160131_1405'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='requires_foi',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='campaign',
            name='search_url',
            field=models.CharField(max_length=1024, blank=True),
        ),
    ]
