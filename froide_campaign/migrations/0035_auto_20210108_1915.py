# Generated by Django 3.1.4 on 2021-01-08 18:15

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("froide_campaign", "0034_auto_20201202_1753"),
    ]

    operations = [
        migrations.AddField(
            model_name="campaignprogresscmsplugin",
            name="count_featured_only",
            field=models.BooleanField(default=False),
        )
    ]
