# Generated by Django 3.0.8 on 2020-11-02 17:09

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('froide_campaign', '0030_auto_20201102_1342'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionaire',
            name='description',
            field=models.TextField(blank=True),
        )
    ]