import os

from django.db import models
from django.conf import settings
from django.utils.translation import gettext as _
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Heartbeat(models.Model):
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'updated at: {}'.format(self.updated_at)
