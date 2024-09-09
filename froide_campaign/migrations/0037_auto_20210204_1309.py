# Generated by Django 3.1.4 on 2021-02-04 12:09

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("froide_campaign", "0036_add_translateable_categories"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="informationobject",
            options={
                "ordering": ("-ordering", "id"),
                "verbose_name": "Information object",
                "verbose_name_plural": "Information objects",
            },
        ),
        migrations.RenameField(
            model_name="informationobject",
            old_name="subtitle",
            new_name="_subtitle",
        ),
        migrations.RenameField(
            model_name="informationobject",
            old_name="title",
            new_name="_title",
        ),
    ]
