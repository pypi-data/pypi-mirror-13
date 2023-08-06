import base64
from django import template

from ..models import Trac
from ..utils import trac_exists
from .. import defaults as defs


register = template.Library()


@register.filter
def is_liked(user, obj):
    """
    True if this object was liked by this user.
    """
    return trac_exists(user, obj, Trac.TRACWARE_TYPE_LIKE)


@register.filter
def is_starred(user, obj):
    """
    True if this object was starred by this user.
    """
    return trac_exists(user, obj, Trac.TRACWARE_TYPE_STAR)


@register.filter
def is_watched(user, obj):
    """
    True if this object was watched by this user.
    """
    return trac_exists(user, obj, Trac.TRACWARE_TYPE_WATCH)


@register.filter
def is_followed(user, obj):
    """
    True if this object was followed by this user.
    """
    return trac_exists(user, obj, Trac.TRACWARE_TYPE_FOLLOW)


@register.filter
def is_bookmarked(user, obj):
    """
    True if this object was bookmarked by this user.
    """
    return trac_exists(user, obj, Trac.TRACWARE_TYPE_BOOKMARK)


@register.filter
def trac_data_tags_initial(instance, trac_type):
    """
    Returns data types for specific type and an object.
    """
    data = _trac_data_tags(instance, trac_type, defs.TRACWARE_STATUS_INIT)
    return data


@register.filter
def trac_data_tags_on(instance, trac_type):
    """
    Returns data types for specific type and an object.
    """
    data = _trac_data_tags(instance, trac_type, defs.TRACWARE_STATUS_ON)
    return data


def _trac_data_tags(instance, trac_type, state):
    """
    Returns data types for specific type and an object.
    """
    data_str = ''
    if instance:
        data = {
            'state': state,
            'type': trac_type,
            'app': instance._meta.app_label,
            'klass': instance.__class__.__name__,
            'pk': instance.id,
        }
        data_str = 'trac-state=%(state)s trac-type=%(type)s trac-app=%(app)s trac-class=%(klass)s trac-oid=%(pk)s' % (data)
    return data_str
