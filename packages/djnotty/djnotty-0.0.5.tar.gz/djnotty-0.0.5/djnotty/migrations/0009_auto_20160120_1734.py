# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('djnotty', '0008_auto_20160118_1730'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messagetouser',
            name='message',
            field=models.ForeignKey(related_name='message_to_user', to='djnotty.Message'),
        ),
        migrations.AlterField(
            model_name='messagetouser',
            name='user',
            field=models.ForeignKey(related_name='messages', to=settings.AUTH_USER_MODEL),
        ),
    ]
