from django.conf import settings

#  allow users to turn template tags autoload off (default 30 days)
TRACWARE_CACHE_ITMEOUT_SECONDS = getattr(settings, 'TRACWARE_CACHE_ITMEOUT_SECONDS', 2592000)

TRACWARE_STATUS_INIT = 'TICK_INIT'
TRACWARE_STATUS_OFF = 'TICK_OFF'
TRACWARE_STATUS_ON = 'TICK_ON'

TRACWARE_TRAC_COUNTER_TYPES = getattr(settings, 'TRACWARE_TRAC_COUNTER_TYPES', [
    'likes',        # others like an object
    'liked',        # an object likes others
    'stars',        # others star and object
    'starred',      # an object stars others
    'watchers',     # others watch an object
    'watching',     # an object watching others
    'followers',    # others follow an object
    'following',    # an object follows others
    'bookmarks',    # others bookmark an object
    'bookmarked',   # an object bookmarks others
])
