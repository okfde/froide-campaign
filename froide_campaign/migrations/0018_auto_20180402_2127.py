# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-04-02 19:27
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('froide_campaign', '0017_auto_20180201_1941'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaignpage',
            name='settings',
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
