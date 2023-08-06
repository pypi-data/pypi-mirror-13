from datetime import timedelta

from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.conf import settings
from model_utils.managers import InheritanceManager
from django.utils.timezone import now
from django.conf import settings


class Message(models.Model):
    XAMI_TYPE = 'original'

    viewed = models.BooleanField(default=False)
    groups = models.ManyToManyField(Group, through='MessageToGroup')
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through='MessageToUser')
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    mark_as_viewed_at = models.DateTimeField(blank=True, null=True, editable=True)
    globally = models.BooleanField(default=False)
    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    stream = models.BooleanField(default=False)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    expires = models.DateTimeField(null=True, blank=True)
    permanent = models.BooleanField(default=False)
    objects = InheritanceManager()

    def for_users(self, users):
        if users:
            for u in users:
                MessageToUser.objects.create(user=u, message=self)

    def for_groups(self, groups):
        if groups:
            for g in groups:
                MessageToGroup.objects.create(group=g, message=self)

    def for_object(self, model):
        cnt = ContentType.objects.get_for_model(model)
        msg = Message()
        msg.content_type = cnt
        msg.object_id = model.pk

    def set_lifetime(self, timedelta_object):
        self.expires = now() + timedelta_object

    def as_json(self):
        return {'text': 'msg', 'stream': False}

    def as_json_for_stream(self):
        return {}

    def save(self, *args, **kwargs):
        if not self.expires and not self.permanent:
            self.set_lifetime(timedelta(days=getattr(settings, 'DJXAMI_MESSAGE_LIFETIME_DAYS', 30)))
        return super(Message, self).save(*args, **kwargs)

    class Meta:
        index_together = (('content_type', 'object_id'),)
        ordering = ['-created_at']
        # abstract = True


class MessageToUser(models.Model):
    message = models.ForeignKey(Message, related_name='message_to_user')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='messages')
    viewed = models.BooleanField(default=False)


class MessageToGroup(models.Model):
    message = models.ForeignKey(Message)
    group = models.ForeignKey(Group)
