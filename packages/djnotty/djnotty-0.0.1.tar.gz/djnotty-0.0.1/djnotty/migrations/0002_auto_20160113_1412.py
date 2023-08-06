# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('djnotty', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='globally',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='message',
            name='mark_as_viewed_at',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
