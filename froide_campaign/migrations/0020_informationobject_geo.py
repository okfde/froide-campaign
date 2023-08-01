# Generated by Django 3.0.8 on 2020-08-11 09:57

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("froide_campaign", "0019_campaignrequestscmsplugin"),
    ]

    operations = [
        migrations.AddField(
            model_name="informationobject",
            name="geo",
            field=django.contrib.gis.db.models.fields.PointField(
                blank=True, geography=True, null=True, srid=4326
            ),
        ),
    ]
