# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-18 15:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("froide_campaign", "0009_auto_20161018_1703"),
    ]

    operations = [
        migrations.AddField(
            model_name="campaign",
            name="category",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
