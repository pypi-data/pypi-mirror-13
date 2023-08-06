# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('djnotty', '0003_auto_20160113_1601'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='driver',
        ),
        migrations.RemoveField(
            model_name='message',
            name='html',
        ),
        migrations.AddField(
            model_name='message',
            name='noty_options',
            field=jsonfield.fields.JSONField(null=True, blank=True),
        ),
    ]
