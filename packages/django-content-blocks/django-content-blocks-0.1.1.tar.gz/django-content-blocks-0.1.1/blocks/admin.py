from django.contrib import admin
from blocks.models import SiteBlock


class SiteBlockAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'block_id', 'url', ]

admin.site.register(SiteBlock, SiteBlockAdmin)
