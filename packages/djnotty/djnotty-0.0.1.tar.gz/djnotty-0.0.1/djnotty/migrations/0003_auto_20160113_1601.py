# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('djnotty', '0002_auto_20160113_1412'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='content_type',
            field=models.ForeignKey(blank=True, to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='message',
            name='object_id',
            field=models.PositiveIntegerField(null=True, blank=True),
        ),
        migrations.AlterIndexTogether(
            name='message',
            index_together=set([('content_type', 'object_id')]),
        ),
        migrations.RemoveField(
            model_name='message',
            name='title',
        ),
    ]
