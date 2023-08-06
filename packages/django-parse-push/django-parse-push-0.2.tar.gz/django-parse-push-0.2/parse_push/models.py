from django.db import models
from django.conf import settings

from enumerify import fields

from .client import get_client
from .enums import DeviceKind
from .managers import DeviceManager


class Device(models.Model):
    """
    USAGE:
        from django.contrib.auth import get_user_model

        User = get_user_model
        user = User.objects.get(email='john@doe.com')
        device = user.device_set.get_latest()
        device.push({'title': 'Hello World!', 'text': 'Lorem ipsum dolor...'})
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    token = models.CharField(max_length=100, unique=True)
    kind = fields.SelectIntegerField(blueprint=DeviceKind, default=DeviceKind.IOS, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    objects = DeviceManager()

    class Meta:
        ordering = ('-created_at',)
        unique_together = (('token', 'kind'), )

    def push(self, data):
        client = get_client()
        return client.push(DeviceKind.get_parse_value(self.kind), self.token, data)
