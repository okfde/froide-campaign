# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("froide_campaign", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="informationobject",
            options={"ordering": ("ordering",)},
        ),
        migrations.AddField(
            model_name="informationobject",
            name="ordering",
            field=models.CharField(max_length=255, blank=True),
        ),
        migrations.AlterField(
            model_name="campaign",
            name="template",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="informationobject",
            name="context",
            field=models.JSONField(blank=True),
        ),
        migrations.AlterField(
            model_name="informationobject",
            name="documents",
            field=models.ManyToManyField(to="foirequest.FoiAttachment", blank=True),
        ),
        migrations.AlterField(
            model_name="informationobject",
            name="foirequest",
            field=models.ForeignKey(
                blank=True,
                to="foirequest.FoiRequest",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
            ),
        ),
        migrations.AlterField(
            model_name="informationobject",
            name="publicbody",
            field=models.ForeignKey(
                blank=True,
                to="publicbody.PublicBody",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
            ),
        ),
    ]
