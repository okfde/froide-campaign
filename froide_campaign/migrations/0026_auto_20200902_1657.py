# Generated by Django 3.0.8 on 2020-09-02 14:57

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('froide_campaign', '0025_auto_20200827_1139'),
    ]

    operations = [
        migrations.AddField(
            model_name='informationobject',
            name='address',
            field=models.TextField(blank=True, verbose_name='Address'),
        )
    ]