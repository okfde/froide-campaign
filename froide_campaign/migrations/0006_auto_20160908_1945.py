# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-08 17:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('froide_campaign', '0005_auto_20160218_1612'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='campaign',
            options={'verbose_name': 'Campaign', 'verbose_name_plural': 'Campaigns'},
        ),
        migrations.AlterModelOptions(
            name='informationobject',
            options={'ordering': ('-ordering', 'title'), 'verbose_name': 'Information object', 'verbose_name_plural': 'Information objects'},
        ),
        migrations.AddField(
            model_name='campaign',
            name='public',
            field=models.BooleanField(default=False),
        ),
    ]