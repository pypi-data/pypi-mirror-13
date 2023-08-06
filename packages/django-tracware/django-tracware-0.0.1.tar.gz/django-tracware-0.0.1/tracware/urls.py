from django.conf.urls import url
from django.conf.urls import patterns

from .views import *


urlpatterns = [

    url(
        r'^toggler/$',
        TracToggleAjaxView.as_view(),
        name='tracware_toggler_ajax_url'
    ),

    url(
        r'^delete/(?P<pk>\d+)$',
        TracDeleteAjaxView.as_view(),
        name='tracware_delete_trac'
    ),

]
