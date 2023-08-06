# coding: utf-8
from __future__ import unicode_literals
from django.core.urlresolvers import reverse


class Builder(object):
    def make(self):
        raise NotImplementedError()


class Linked(Builder):
    script_name = 'djnotty_linked'

    def __init__(self, url):
        self.url = url

    def make(self, opts):
        opts.update({'linked': self.url})
        return opts


class Close(Builder):
    script_name = 'djnotty_close'

    def __init__(self, url=None):
        self.url = url

    def make(self, opts):
        opts.update({'url': reverse('djnotty:close')})
        if self.url:
            opts['linked'] = self.url

        return opts


class Text(Builder):
    def __init__(self, text):
        self.text = text

    def make(self, opts):
        opts.update({'text': self.text})

        return opts
