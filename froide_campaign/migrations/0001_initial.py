# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import parler


class Migration(migrations.Migration):

    dependencies = [
        ('foirequest', '0002_auto_20150728_1829'),
        ('publicbody', '0003_auto_20160123_1336'),
    ]

    operations = [
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('slug', models.SlugField()),
                ('template', models.TextField()),
            ],
            bases=(parler.models.TranslatableModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='InformationObject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ident', models.CharField(max_length=255)),
                ('title', models.CharField(max_length=1000)),
                ('slug', models.SlugField()),
                ('context', models.JSONField()),
                ('campaign', models.ForeignKey(to='froide_campaign.Campaign', on_delete=django.db.models.deletion.CASCADE)),
                ('documents', models.ManyToManyField(to='foirequest.FoiAttachment')),
                ('foirequest', models.ForeignKey(to='foirequest.FoiRequest', null=True, on_delete=django.db.models.deletion.SET_NULL)),
                ('publicbody', models.ForeignKey(to='publicbody.PublicBody', null=True, on_delete=django.db.models.deletion.SET_NULL)),
            ],
            bases=(parler.models.TranslatableModelMixin, models.Model),
        ),
    ]
