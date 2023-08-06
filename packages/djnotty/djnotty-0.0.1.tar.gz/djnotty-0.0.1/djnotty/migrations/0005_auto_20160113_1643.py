# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('djnotty', '0004_auto_20160113_1614'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='noty_options',
        ),
        migrations.RemoveField(
            model_name='messagetogroup',
            name='viewed',
        ),
        migrations.AddField(
            model_name='message',
            name='script',
            field=models.TextField(null=True, blank=True),
        ),
    ]
