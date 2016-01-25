from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from froide.helper.admin_utils import make_nullfilter

from .models import Campaign, InformationObject


class CampaignAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}


class InformationObjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'ident', 'publicbody', 'foirequest',)
    list_filter = ('campaign', 'foirequest__status', 'foirequest__resolution',
                    make_nullfilter('foirequest', _(u'Has request')),
                    make_nullfilter('documents', _(u'Has documents')),
                    make_nullfilter('publicbody', _(u'Has public body'))
    )
    raw_id_fields = ('publicbody', 'foirequest', 'documents')
    search_fields = ('title', 'ident')


admin.site.register(Campaign, CampaignAdmin)
admin.site.register(InformationObject, InformationObjectAdmin)
