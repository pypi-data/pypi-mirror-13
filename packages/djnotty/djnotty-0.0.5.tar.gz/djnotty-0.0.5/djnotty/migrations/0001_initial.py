# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        (b'auth', b'__first__'),
        (b'contenttypes', b'__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('html', models.TextField()),
                ('viewed', models.BooleanField(default=False)),
                ('driver', models.CharField(max_length=200, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='MessageToGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('viewed', models.BooleanField(default=False)),
                ('group', models.ForeignKey(to='auth.Group')),
                ('message', models.ForeignKey(to='djnotty.Message')),
            ],
        ),
        migrations.CreateModel(
            name='MessageToUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('viewed', models.BooleanField(default=False)),
                ('message', models.ForeignKey(to='djnotty.Message')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='message',
            name='groups',
            field=models.ManyToManyField(to='auth.Group', through='djnotty.MessageToGroup'),
        ),
        migrations.AddField(
            model_name='message',
            name='users',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, through='djnotty.MessageToUser'),
        ),
    ]
