
from django.conf import settings
from django.db.models import signals
from django.apps import apps
from django.db import DEFAULT_DB_ALIAS

from .models import Heartbeat


def post_migrate_receiver(app_config, verbosity=2, interactive=False, using=DEFAULT_DB_ALIAS, **kwargs):
    """
    Finalize the website loading.
    """
    Heartbeat.objects.get_or_create(id=1)
