# coding: utf-8
from __future__ import unicode_literals

from operator import or_

from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django.views import generic
from djnotty import models
from django.db.models import Q
from django.conf import settings
from django.utils.timezone import now
from datetime import timedelta
import json


class Messages(generic.View):
    def get_queryset(self):
        qs = models.Message.objects

        flt = [Q(globally=True)]

        if self.request.user.is_authenticated():
            qs = qs.filter(~Q(message_to_user__in=models.MessageToUser.objects.filter(user=self.request.user, viewed=True)))
            flt.append(Q(groups__in=self.request.user.groups.all()))
            # qs = qs | qs.filter(~Q(message_to_user__in=models.MessageToUser.objects.filter(user=self.request.user, viewed=True)))
            # qs = qs | qs.filter(Q(groups__in=self.request.user.groups.all()) | Q(globally=True))
        return qs.filter(reduce(or_, flt))

    def get(self, *args, **kwargs):
        messages = []
        for message in self.get_queryset()[:10]:
            messages.append({'opts': message.noty_options, 'builders': message.builders.split(','), 'id': message.pk})

        return HttpResponse(json.dumps(messages), content_type='application/json')


class Close(generic.View):
    model = models.Message

    def post(self, *args, **kwargs):
        response = HttpResponse(json.dumps({'status': 'success'}), content_type='application/json')
        message = get_object_or_404(models.Message, pk=int(self.request.POST.get('id')))
        if self.request.user.is_authenticated():
            try:
                rel = models.MessageToUser.objects.get(user=self.request.user, message=message)
            except models.MessageToUser.DoesNotExist:
                rel = models.MessageToUser(user=self.request.user, message=message)

            rel.viewed = True
            rel.save()
        else:
            viewed = [unicode(message.pk)]
            in_cookies = self.request.COOKIES.get('djnotty', None)
            if in_cookies and len(in_cookies) < 1000:
                viewed += in_cookies.split(':')
            print viewed
            response.set_cookie('djnotty',
                                str(':'.join(set(viewed))),
                                expires=now() + timedelta(days=365),
                                domain=settings.SESSION_COOKIE_DOMAIN,
                                secure=settings.SESSION_COOKIE_SECURE or None)

        return response
