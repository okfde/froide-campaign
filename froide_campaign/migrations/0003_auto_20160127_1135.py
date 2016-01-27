# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('froide_campaign', '0002_auto_20160123_1454'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='informationobject',
            options={'ordering': ('-ordering',)},
        ),
        migrations.AddField(
            model_name='campaign',
            name='description',
            field=models.TextField(blank=True),
        ),
    ]
