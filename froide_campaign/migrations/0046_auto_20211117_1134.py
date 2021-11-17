# Generated by Django 3.2.8 on 2021-11-17 10:34

from django.conf import settings
import django.contrib.postgres.search
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("froide_campaign", "0045_auto_20210215_1040"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="question",
            options={"ordering": ["questionaire", "position", "id"]},
        ),
        migrations.AddField(
            model_name="question",
            name="data_type",
            field=models.CharField(
                choices=[("", "Text"), ("choices", "Choices"), ("integer", "Integer")],
                default="",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="question",
            name="position",
            field=models.SmallIntegerField(
                blank=True, default=0, verbose_name="Position"
            ),
        ),
        migrations.AddField(
            model_name="report",
            name="timestamp",
            field=models.DateTimeField(default=django.utils.timezone.now, null=True),
        ),
        migrations.AddField(
            model_name="report",
            name="user",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
                verbose_name="User",
            ),
        ),
        migrations.AlterField(
            model_name="informationobject",
            name="search_vector",
            field=django.contrib.postgres.search.SearchVectorField(
                default="", editable=False
            ),
        ),
        migrations.AlterField(
            model_name="question",
            name="options",
            field=models.TextField(blank=True),
        ),
    ]
