import csv
import io
from datetime import timedelta

from django.http import HttpResponse
from django.contrib import admin
from django.contrib import messages
from django import forms
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.conf.urls import url
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from django.db.models import Count

from parler.admin import TranslatableAdmin

from froide.helper.admin_utils import make_nullfilter
from froide.helper.csv_utils import export_csv_response
from froide.georegion.models import GeoRegion

from .models import (CampaignPage, Campaign, InformationObject,
                     CampaignSubscription,
                     Questionaire, Question, Report, Answer, CampaignCategory)
from .utils import CSVImporter


class CampaignPageAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    raw_id_fields = ('user', 'team')


class CampaignAdmin(TranslatableAdmin):
    list_filter = (
        'provider',
        'public',
        'requires_foi',
        'paused',
    )

    def get_prepopulated_fields(self, request, obj=None):
        # can't use `prepopulated_fields = ..` because it breaks the admin validation
        # for translated fields. This is the official django-parler workaround.
        return {
            'slug': ('title',)
        }


class CampaignSubscriptionsAdmin(admin.ModelAdmin):
    list_filter = ('campaign',)
    list_display = ('campaign', 'email')


class InformationObjectAdmin(TranslatableAdmin):
    list_display = ('title',
                    'ident', 'campaign', 'publicbody',
                    'request_count', 'featured')
    list_filter = (
        'campaign', 'foirequest__status', 'foirequest__resolution',
        'resolved', 'featured',
        make_nullfilter('foirequest', _('Has request')),
        make_nullfilter('documents', _('Has documents')),
        make_nullfilter('publicbody', _('Has public body')),
        make_nullfilter('geo', _('Has geo'))
    )
    raw_id_fields = (
        'publicbody', 'foirequest', 'foirequests', 'documents'
    )
    search_fields = ('translations__title', 'ident')

    actions = [
        'clean_requests', 'resolve_requests', 'export_csv',
        'update_search_index'
    ]

    def get_prepopulated_fields(self, request, obj=None):
        # can't use `prepopulated_fields = ..` because it breaks the admin
        # validation for translated fields. This is the official django-parler
        # workaround.
        return {
            'slug': ('title',)
        }

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(
            request_count=Count('foirequests')
        )
        qs = qs.select_related('publicbody')
        return qs

    def request_count(self, obj):
        return obj.request_count
    request_count.admin_order_field = 'request_count'
    request_count.short_description = _('requests')

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

        importer = CSVImporter(request)
        csv_file = request.FILES['file']
        file = csv_file.read().decode('utf-8')
        io_string = io.StringIO(file)
        io_string.seek(0)
        reader = csv.DictReader(io_string)
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


class QuestionForm(forms.ModelForm):

    class Meta:
        fields = '__all__'
        model = Question


class QuestionInline(admin.TabularInline):
    model = Question
    form = QuestionForm
    extra = 0
    min_num = 0


class CampaignQuestionaireAdmin(admin.ModelAdmin):
    list_filter = ('campaign',)
    list_display = ('campaign', 'title')
    inlines = [
        QuestionInline
    ]


class AnswerForm(forms.ModelForm):

    class Meta:
        fields = '__all__'
        model = Answer


class AnswerInline(admin.TabularInline):
    model = Answer
    form = AnswerForm
    extra = 0
    min_num = 0


class CampaignReportAdmin(admin.ModelAdmin):
    raw_id_fields = ('informationsobject',)
    list_filter = ('questionaire',)
    inlines = [
        AnswerInline
    ]

    actions = [
        'export_csv'
    ]

    def get_zipcode(self, point):
        zip_codes = GeoRegion.objects.filter(kind='zipcode')
        zip_code = zip_codes.filter(geom__bboverlaps=point)
        if zip_code:
            return zip_code.first().description
        return ''

    def export_csv(self, request, queryset):
        questionaire_ids = queryset.values_list('questionaire_id', flat=True)
        if len(set(questionaire_ids)) > 1:
            msg = 'You can only export reports from the same questionaire'
            self.message_user(request, msg, level=messages.ERROR)
        else:
            q_id = questionaire_ids[0]
            questionaire = Questionaire.objects.get(id=q_id)
            questions = questionaire.question_set.all()

            content = 'attachment; filename="{}_{}.csv"'.format(
                questionaire.title, timezone.now())

            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = content
            writer = csv.writer(response)

            header = ['Name', 'URL', 'Datum', 'PLZ'] + [question.text
                                        for question in questions]
            writer.writerow(header)
            for report in queryset:
                iobject = report.informationsobject
                zipcode = ''
                foirequest = iobject.get_best_foirequest()
                if iobject.geo:
                    zipcode = self.get_zipcode(iobject.geo)
                infooject_details = [
                    iobject.translations_title,
                    foirequest.get_absolute_domain_short_url(),
                    foirequest.messages[0].timestamp.date(),
                    zipcode
                ]
                answer_texts = []
                for question in questions:
                    answers = report.answer_set.all()
                    text = answers.get(question=question).text
                    answer_texts.append(text)
                row = infooject_details + answer_texts
                writer.writerow(row)
            return response

    export_csv.short_description = _("Export to CSV")


class CategoryAdmin(TranslatableAdmin):
    fields = ('title', 'description', 'slug')
    list_display = ('title',)
    search_fields = ('translations__title', 'translations__description')
    list_filter = ('information_objects__campaign', )

    def get_prepopulated_fields(self, request, obj=None):
        # can't use `prepopulated_fields = ..` because it breaks the admin
        # validation for translated fields. This is the official django-parler
        # workaround.
        return {
            'slug': ('title',)
        }


admin.site.register(CampaignPage, CampaignPageAdmin)
admin.site.register(Campaign, CampaignAdmin)
admin.site.register(InformationObject, InformationObjectAdmin)
admin.site.register(CampaignSubscription, CampaignSubscriptionsAdmin)
admin.site.register(Questionaire, CampaignQuestionaireAdmin)
admin.site.register(Report, CampaignReportAdmin)
admin.site.register(CampaignCategory, CategoryAdmin)
