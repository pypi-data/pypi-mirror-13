# coding: utf-8
from __future__ import unicode_literals
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.conf import settings
from jsonfield import JSONField


class MessageObjects(models.Manager):
    def make_message(self, msg, builders, globally=False, users=None, groups=None):
        if users or groups:
            globally = False
        noty_opts = {}
        scripts = []
        for b in builders:
            noty_opts = b.make(noty_opts)
            if hasattr(b, 'script_name'):
                scripts.append(b.script_name)

        msg.noty_options = noty_opts
        msg.globally = globally
        msg.builders = ','.join(scripts)
        msg.save()
        if users:
            for u in users:
                MessageToUser.objects.create(user=u, message=msg)

        if groups:
            for g in groups:
                MessageToGroup.objects.create(group=g, message=msg)
        return msg

    def create_for_object(self, model, **kwargs):
        cnt = ContentType.objects.get_for_model(model)
        msg = Message()

        msg.content_type = cnt
        msg.object_id = model.pk
        print kwargs
        self.make_message(msg, **kwargs)
        msg.save()

    def create_globally(self, builders):
        return self.make_message(Message(), builders, globally=True)

    def mark_as_viewed_for_object(self, model, user=None):
        cnt = ContentType.objects.get_for_model(model)
        if user:
            MessageToUser.objects.filter(message__content_type=cnt, message__object_id=model.pk, user=user).update(viewed=True)
        else:
            Message.objects.filter(content_type=cnt, object_id=model.pk).update(viewed=True)


class Message(models.Model):
    viewed = models.BooleanField(default=False)
    groups = models.ManyToManyField(Group, through='MessageToGroup')
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through='MessageToUser')
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    mark_as_viewed_at = models.DateTimeField(blank=True, null=True, editable=True)
    globally = models.BooleanField(default=False)

    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    builders = models.CharField(max_length=500, blank=True)
    noty_options = JSONField(blank=True, null=True)
    objects = MessageObjects()

    class Meta:
        index_together = (('content_type', 'object_id'))


class MessageToUser(models.Model):
    message = models.ForeignKey(Message, related_name='message_to_user')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='messages')
    viewed = models.BooleanField(default=False)


class MessageToGroup(models.Model):
    message = models.ForeignKey(Message)
    group = models.ForeignKey(Group)
