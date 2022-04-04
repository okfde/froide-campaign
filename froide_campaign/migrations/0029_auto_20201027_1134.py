# Generated by Django 3.0.8 on 2020-10-27 10:34

import django.contrib.postgres.fields.jsonb
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cms", "0022_auto_20180620_1551"),
        ("froide_campaign", "0028_auto_20200923_2058"),
    ]

    operations = [
        migrations.CreateModel(
            name="Questionaire",
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
            ],
        ),
        migrations.CreateModel(
            name="Report",
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
                    "informationsobject",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="froide_campaign.InformationObject",
                    ),
                ),
                (
                    "questionaire",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="froide_campaign.Questionaire",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="questionaire",
            name="campaign",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="froide_campaign.Campaign",
            ),
        ),
        migrations.CreateModel(
            name="Question",
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
                ("text", models.CharField(max_length=255)),
                ("is_required", models.BooleanField(default=False)),
                ("options", models.CharField(blank=True, max_length=255)),
                ("help_text", models.CharField(blank=True, max_length=255)),
                (
                    "questionaire",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="froide_campaign.Questionaire",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="CampaignQuestionaireCMSPlugin",
            fields=[
                (
                    "cmsplugin_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        related_name="froide_campaign_campaignquestionairecmsplugin",
                        serialize=False,
                        to="cms.CMSPlugin",
                    ),
                ),
                (
                    "questionaire",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="froide_campaign.Questionaire",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("cms.cmsplugin",),
        ),
        migrations.CreateModel(
            name="Answer",
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
                ("text", models.CharField(max_length=255)),
                (
                    "question",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="froide_campaign.Question",
                    ),
                ),
                (
                    "report",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="froide_campaign.Report",
                    ),
                ),
            ],
        ),
    ]
