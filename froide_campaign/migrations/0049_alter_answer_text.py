# Generated by Django 3.2.8 on 2021-12-16 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("froide_campaign", "0048_auto_20211117_1446"),
    ]

    operations = [
        migrations.AlterField(
            model_name="answer",
            name="text",
            field=models.TextField(blank=True),
        ),
    ]
