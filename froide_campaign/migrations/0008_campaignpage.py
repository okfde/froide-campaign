# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-18 15:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("froide_campaign", "0007_campaign_subject_template"),
    ]

    operations = [
        migrations.CreateModel(
            name="CampaignPage",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("slug", models.SlugField()),
                ("description", models.TextField(blank=True)),
                ("public", models.BooleanField(default=False)),
                ("campaigns", models.ManyToManyField(to="froide_campaign.Campaign")),
            ],
            options={
                "verbose_name": "Campaign page",
                "verbose_name_plural": "Campaign pages",
            },
        ),
    ]
