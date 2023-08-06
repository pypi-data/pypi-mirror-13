from django.conf import settings
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import gettext as _

from . import defaults as defs


@python_2_unicode_compatible
class Trac(models.Model):
    """
    Trac(k) objects for this user.
    """
    TRACWARE_TYPE_LIKE = "Like"
    TRACWARE_TYPE_STAR = "Star"
    TRACWARE_TYPE_WATCH = "Watch"
    TRACWARE_TYPE_FOLLOW = "Follow"
    TRACWARE_TYPE_BOOKMARK = "Bookmark"
    TRACWARE_TYPE_OPTIONS = (
        (TRACWARE_TYPE_LIKE, TRACWARE_TYPE_LIKE),
        (TRACWARE_TYPE_STAR, TRACWARE_TYPE_STAR),
        (TRACWARE_TYPE_WATCH, TRACWARE_TYPE_WATCH),
        (TRACWARE_TYPE_FOLLOW, TRACWARE_TYPE_FOLLOW),
        (TRACWARE_TYPE_BOOKMARK, TRACWARE_TYPE_BOOKMARK),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="%(class)s")
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    trac_type = models.CharField(choices=TRACWARE_TYPE_OPTIONS, max_length=20)

    class Meta:
        verbose_name = _('trac')
        verbose_name_plural = _('tracs')
        unique_together = (('user', 'content_type', 'object_id', 'trac_type'),)

    def __str__(self):
        return u'{0}-[{1}]'.format(self.user, self.content_object)
