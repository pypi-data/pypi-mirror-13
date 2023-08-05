from django.apps import apps
from django.db.models import signals
from django.apps import AppConfig as DjangoAppConfig
from django.utils.translation import ugettext_lazy as _


class AppConfig(DjangoAppConfig):
    """
    Configuration entry point for the pulseware app
    """
    label = name = 'pulseware'
    verbose_name = _("pulseware app")

    def ready(self):
        """
        Create one object
        """
        from . import receivers as rcvs
        signals.post_migrate.connect(rcvs.post_migrate_receiver,
            sender=apps.get_app_config(self.name))
