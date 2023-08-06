
from django.db import models


class DeviceManager(models.Manager):

    def get_latest(self):
        """ Returns latest Device instance """
        return self.get_queryset().latest('created_at')

    def get_last_used(self):
        """ Returns last used Device instance """
        return self.get_queryset().latest('updated_at')
