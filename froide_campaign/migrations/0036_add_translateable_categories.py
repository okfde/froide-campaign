# Generated by Django 3.1.4 on 2021-02-03 12:14

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import parler.fields
import parler.models


class Migration(migrations.Migration):

    dependencies = [
        ('froide_campaign', '0035_auto_20210108_1915'),
    ]

    operations = [
        migrations.CreateModel(
            name='CampaignCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'category',
                'verbose_name_plural': 'categories',
            },
            bases=(parler.models.TranslatableModelMixin, models.Model),
        ),
        migrations.AddField(
            model_name='campaign',
            name='categories',
            field=models.ManyToManyField(blank=True, related_name='campaigns', to='froide_campaign.CampaignCategory', verbose_name='categories'),
        ),
        migrations.AddField(
            model_name='informationobject',
            name='categories',
            field=models.ManyToManyField(blank=True, related_name='information_objects', to='froide_campaign.CampaignCategory', verbose_name='categories'),
        ),
        migrations.CreateModel(
            name='CampaignCategoryTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('title', models.CharField(max_length=255, verbose_name='title')),
                ('slug', models.SlugField(help_text="Used to build the category's URL.", max_length=255, verbose_name='slug')),
                ('description', models.TextField(blank=True, verbose_name='description')),
                ('master', parler.fields.TranslationsForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='froide_campaign.campaigncategory')),
            ],
            options={
                'verbose_name': 'category Translation',
                'db_table': 'froide_campaign_campaigncategory_translation',
                'db_tablespace': '',
                'managed': True,
                'default_permissions': (),
                'unique_together': {('language_code', 'master')},
            },
            bases=(parler.models.TranslatableModel, models.Model),
        ),
    ]