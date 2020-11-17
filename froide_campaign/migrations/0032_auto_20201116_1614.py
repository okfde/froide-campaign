# Generated by Django 3.0.8 on 2020-11-16 15:14

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('froide_campaign', '0031_auto_20201102_1809'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='tags',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='informationobject',
            name='tags',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=list),
        )
    ]
