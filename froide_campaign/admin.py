from datetime import timedelta

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

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

    actions = ['clean_requests']

    def clean_requests(self, request, queryset):
        from froide.foirequest.models import FoiRequest

        queryset = queryset.filter(foirequest__isnull=False)
        a_day_ago = timezone.now() - timedelta(days=1)
        queryset = queryset.filter(foirequest__firstmessage__lt=a_day_ago)
        queryset.exclude(
            foirequest__visibility=FoiRequest.VISIBLE_TO_PUBLIC
        ).update(foirequest=None)
        return None
    clean_requests.short_description = _("Clean out bad requests")


admin.site.register(Campaign, CampaignAdmin)
admin.site.register(InformationObject, InformationObjectAdmin)
