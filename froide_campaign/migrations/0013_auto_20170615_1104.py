# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-15 09:04
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('froide_campaign', '0012_auto_20161020_1243'),
    ]

    operations = [
        migrations.AlterField(
            model_name='informationobject',
            name='context',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True),
        ),
    ]
