# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models, migrations


def clear_messages(apps, schema_editor):
    m = apps.get_model('djnotty', 'Message')
    print m.objects.count()
    m.objects.all().delete()
    print m.objects.count()


class Migration(migrations.Migration):
    dependencies = [
        ('djnotty', '0007_message_builders'),
    ]

    operations = [
        migrations.RunPython(clear_messages)
    ]
