# coding: utf-8
from __future__ import unicode_literals
from django.core.urlresolvers import reverse


class Builder(object):
    stream = False

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

    def __init__(self, redirect=None):
        self.redirect = redirect

    def make(self, opts):
        if self.redirect:
            opts['redirect'] = self.redirect

        return opts


class Text(Builder):
    def __init__(self, text):
        self.text = text

    def make(self, opts):
        opts.update({'text': self.text})

        return opts


class ProgressBar(Builder):
    stream = True
    script_name = 'djnotty_progressbar'

    def __init__(self, text, current=0):
        self.current = current
        self.text = text

    def make(self, opts):
        opts.update({
            'current': self.current,
            'layout': 'bottomLeft',
            'type': 'alert',
            'template': '''
                <div class="noty_messsage">
                    <div class="progress">
                        <div class="progress-bar" role="progressbar" aria-valuenow="%s" aria-valuemin="0" aria-valuemax="100" style="width: %s%%;">
                            <span class="noty_text"></span>
                        </div>
                    </div>
                </div>
            ''' % (self.current, self.current),
            'text': ' %s%% - %s' % (self.current, self.text)

        })
        return opts
