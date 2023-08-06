from django.contrib import admin

from .models import Trac


class TracAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'user',
        'content_type',
        'object_id',
        'content_object',
        'trac_type',
    )

    search_fields = [
        'id',
        'user',
        'content_type',
        'object_id',
        'content_object',
        'trac_type',
    ]

    list_per_page = 25

admin.site.register(Trac, TracAdmin)
