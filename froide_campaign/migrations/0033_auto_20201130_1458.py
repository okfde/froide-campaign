# Generated by Django 3.0.8 on 2020-11-30 13:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("froide_campaign", "0032_auto_20201116_1614"),
    ]

    operations = [
        migrations.AddField(
            model_name="informationobject",
            name="featured",
            field=models.BooleanField(default=False),
        )
    ]
