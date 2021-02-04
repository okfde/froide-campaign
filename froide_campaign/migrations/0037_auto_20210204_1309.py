# Generated by Django 3.1.4 on 2021-02-04 12:09

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('froide_campaign', '0036_add_translateable_categories'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='informationobject',
            options={'ordering': ('-ordering', '_title'), 'verbose_name': 'Information object', 'verbose_name_plural': 'Information objects'},
        ),
        migrations.RenameField(
            model_name='informationobject',
            old_name='subtitle',
            new_name='_subtitle',
        ),
        migrations.RenameField(
            model_name='informationobject',
            old_name='title',
            new_name='_title',
        )
    ]
