from django.apps import apps
from django.db.models import signals
from django.utils.translation import gettext as _
from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    """
    Configuration entry point for the tracware app
    """
    label = name = 'tracware'
    verbose_name = _("tracware app")

    def ready(self):
            """
            App is imported and ready, so bootstrap it.
            """
            from . import utils as util

            signals.pre_delete.connect(util.trac_delete_trac_for_object,
                sender=apps.get_app_config(self.name))
