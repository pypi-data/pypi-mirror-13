from django.dispatch import Signal

trac_created = Signal(providing_args=["request, trac"])
trac_deleted = Signal(providing_args=["request, trac"])
