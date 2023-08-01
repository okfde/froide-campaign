# Generated by Django 3.1.6 on 2021-02-08 14:30

import django.db.models.deletion
from django.db import migrations, models

import parler.fields
import parler.models


class Migration(migrations.Migration):
    dependencies = [
        ("froide_campaign", "0040_auto_20210204_1528"),
    ]

    operations = [
        migrations.RenameField(
            model_name="campaign",
            old_name="description",
            new_name="_description",
        ),
        migrations.RenameField(
            model_name="campaign",
            old_name="slug",
            new_name="_slug",
        ),
        migrations.RenameField(
            model_name="campaign",
            old_name="subject_template",
            new_name="_subject_template",
        ),
        migrations.RenameField(
            model_name="campaign",
            old_name="template",
            new_name="_template",
        ),
        migrations.RenameField(
            model_name="campaign",
            old_name="title",
            new_name="_title",
        ),
        migrations.AlterField(
            model_name="campaign",
            name="provider",
            field=models.CharField(
                blank=True,
                choices=[
                    ("", "froide_campaign.providers.base.BaseProvider"),
                    ("amenity", "froide_campaign.providers.amenity.AmenityProvider"),
                    (
                        "publicbody",
                        "froide_campaign.providers.publicbody.PublicBodyProvider",
                    ),
                    (
                        "amenity_local",
                        "froide_campaign.providers.amenity_local.AmenityLocalProvider",
                    ),
                ],
                max_length=40,
            ),
        ),
        migrations.AlterField(
            model_name="informationobject",
            name="context",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.CreateModel(
            name="CampaignTranslation",
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
                (
                    "language_code",
                    models.CharField(
                        db_index=True, max_length=15, verbose_name="Language"
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("slug", models.SlugField()),
                ("description", models.TextField(blank=True)),
                ("subject_template", models.CharField(blank=True, max_length=255)),
                ("template", models.TextField(blank=True)),
                (
                    "master",
                    parler.fields.TranslationsForeignKey(
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="translations",
                        to="froide_campaign.campaign",
                    ),
                ),
            ],
            options={
                "verbose_name": "Campaign Translation",
                "db_table": "froide_campaign_campaign_translation",
                "db_tablespace": "",
                "managed": True,
                "default_permissions": (),
                "unique_together": {("language_code", "master")},
            },
            bases=(parler.models.TranslatedFieldsModelMixin, models.Model),
        ),
    ]
