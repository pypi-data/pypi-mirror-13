from djxami.models import Message
from jsonfield import JSONField
from django.db import models


class NottyMessage(Message):
    XAMI_TYPE = 'djnotty'
    scripts = models.CharField(max_length=500, blank=True)
    notty_options = JSONField(blank=True, null=True)

    def builders(self, builders):
        notty_opts = {}
        scripts = []
        for b in builders:
            if b.stream is True:
                self.stream = True

            notty_opts = b.make(notty_opts)
            if hasattr(b, 'script_name'):
                scripts.append(b.script_name)

        self.notty_options = notty_opts
        self.scripts = ','.join(scripts) if scripts else ''

    def apply_builder(self, builder, commit=True):
        self.notty_options.update(builder.make(self.notty_options))
        if commit:
            self.save()

    def as_json(self):
        return {'opts': self.notty_options, 'scripts': self.scripts.split(','), 'id': self.pk}

    def as_json_for_stream(self):
        return self.as_json()
