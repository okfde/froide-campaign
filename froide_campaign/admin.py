from datetime import timedelta

from django.contrib import admin
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.conf.urls import url
from django.utils import timezone
from django.core.exceptions import PermissionDenied

import unicodecsv

from froide.helper.admin_utils import make_nullfilter
from froide.helper.csv_utils import export_csv_response

from .models import CampaignPage, Campaign, InformationObject
from .utils import CSVImporter


class CampaignPageAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    raw_id_fields = ('user', 'team')


class CampaignAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}


class InformationObjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'ident', 'campaign', 'publicbody', 'foirequest',)
    list_filter = (
        'campaign', 'foirequest__status', 'foirequest__resolution',
        'resolved',
        make_nullfilter('foirequest', _('Has request')),
        make_nullfilter('documents', _('Has documents')),
        make_nullfilter('publicbody', _('Has public body'))
    )
    raw_id_fields = (
        'publicbody', 'foirequest', 'foirequests', 'documents'
    )
    search_fields = ('title', 'ident')

    actions = ['clean_requests', 'resolve_requests', 'export_csv', 'update_search_index']

    def get_urls(self):
        urls = super(InformationObjectAdmin, self).get_urls()
        my_urls = [
            url(r'^upload/$',
                self.admin_site.admin_view(self.upload_information_objects),
                name='froide_campaign-admin_upload'),
        ]
        return my_urls + urls

    def export_csv(self, request, queryset):
        queryset = queryset.select_related('foirequest', 'publicbody')
        csv_generator = InformationObject.objects.export_csv(queryset)
        return export_csv_response(csv_generator)
    export_csv.short_description = _("Export to CSV")

    def update_search_index(self, request, queryset):
        InformationObject.objects.update_search_index(qs=queryset)

    def upload_information_objects(self, request):
        if not request.method == 'POST':
            raise PermissionDenied
        if not self.has_change_permission(request):
            raise PermissionDenied
        reader = unicodecsv.DictReader(request.FILES['file'])
        importer = CSVImporter()
        importer.run(reader)
        return redirect('admin:froide_campaign_informationobject_changelist')

    def resolve_requests(self, request, queryset):
        queryset = queryset.filter(foirequest__isnull=False)
        queryset = queryset.select_related('foirequest')
        for iobj in queryset:
            if iobj.foirequest is None:
                continue
            iobj.foirequest.status = 'resolved'
            iobj.foirequest.resolution = 'successful'
            iobj.foirequest.save()
        return None
    resolve_requests.short_description = _("Mark requests as "
                                           "successfully resolved")

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
