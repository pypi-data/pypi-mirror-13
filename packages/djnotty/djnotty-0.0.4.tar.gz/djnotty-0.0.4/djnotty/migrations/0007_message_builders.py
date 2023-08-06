# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('djnotty', '0006_auto_20160113_1656'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='builders',
            field=models.CharField(max_length=500, blank=True),
        ),
    ]
