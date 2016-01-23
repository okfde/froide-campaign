from django.contrib import admin

from .models import Campaign, InformationObject


class CampaignAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}


class InformationObjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'publicbody', 'foirequest',)
    raw_id_fields = ('publicbody', 'foirequest', 'documents')
    search_fields = ('title',)


admin.site.register(Campaign, CampaignAdmin)
admin.site.register(InformationObject, InformationObjectAdmin)
