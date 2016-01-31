# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('froide_campaign', '0003_auto_20160127_1135'),
    ]

    operations = [
        migrations.AlterField(
            model_name='informationobject',
            name='foirequest',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='foirequest.FoiRequest', null=True),
        ),
        migrations.AlterField(
            model_name='informationobject',
            name='publicbody',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='publicbody.PublicBody', null=True),
        ),
    ]
