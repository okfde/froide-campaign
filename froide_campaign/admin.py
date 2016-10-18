from datetime import timedelta

from django.contrib import admin
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.conf.urls import url
from django.utils import timezone
from django.core.exceptions import PermissionDenied

import unicodecsv

from froide.helper.admin_utils import make_nullfilter

from .models import CampaignPage, Campaign, InformationObject
from .utils import CSVImporter


class CampaignPageAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}


class CampaignAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}


class InformationObjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'ident', 'campaign', 'publicbody', 'foirequest',)
    list_filter = ('campaign', 'foirequest__status', 'foirequest__resolution',
                    make_nullfilter('foirequest', _(u'Has request')),
                    make_nullfilter('documents', _(u'Has documents')),
                    make_nullfilter('publicbody', _(u'Has public body'))
    )
    raw_id_fields = ('publicbody', 'foirequest', 'documents')
    search_fields = ('title', 'ident')

    actions = ['clean_requests']

    def get_urls(self):
        urls = super(InformationObjectAdmin, self).get_urls()
        my_urls = [
            url(r'^upload/$',
                self.admin_site.admin_view(self.upload_information_objects),
                name='froide_campaign-admin_upload'),
        ]
        return my_urls + urls

    def upload_information_objects(self, request):
        if not request.method == 'POST':
            raise PermissionDenied
        if not self.has_change_permission(request):
            raise PermissionDenied
        reader = unicodecsv.DictReader(request.FILES['file'])
        importer = CSVImporter()
        importer.run(reader)
        return redirect('admin:froide_campaign_informationobject_changelist')

    def clean_requests(self, request, queryset):
        queryset = queryset.filter(foirequest__isnull=False)
        queryset = queryset.select_related('foirequest')
        a_day_ago = timezone.now() - timedelta(days=1)
        for iobj in queryset:
            if iobj.foirequest is None:
                continue
            if iobj.foirequest.first_message >= a_day_ago:
                continue
            if iobj.foirequest.is_visible():
                continue
            iobj.foirequest = None
            iobj.save()
        return None
    clean_requests.short_description = _("Clean out bad requests")


admin.site.register(CampaignPage, CampaignPageAdmin)
admin.site.register(Campaign, CampaignAdmin)
admin.site.register(InformationObject, InformationObjectAdmin)
