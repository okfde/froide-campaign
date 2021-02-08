import json
import logging

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.templatetags.static import static
from django.utils.translation import gettext_lazy as _
from django.utils.translation import get_language

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from froide.foirequest.models.request import Resolution
from froide.foirequest.models.request import FoiRequest
from froide.foirequest.views import MakeRequestView

from .models import (CampaignRequestsCMSPlugin,
                     InformationObject,
                     CampaignSubscription,
                     CampaignCMSPlugin,
                     CampaignQuestionaireCMSPlugin,
                     CampaignProgressCMSPlugin
                     )

from .providers import BaseProvider

try:
    from django.contrib.gis.geoip2 import GeoIP2
except ImportError:
    GeoIP2 = None

from froide.helper.utils import get_client_ip

logger = logging.getLogger(__name__)


@plugin_pool.register_plugin
class CampaignRequestsPlugin(CMSPluginBase):
    module = _("Campaign")
    name = _("Campaign Requests")
    render_template = "froide_campaign/plugins/campaign_requests.html"
    model = CampaignRequestsCMSPlugin

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)
        campaigns = instance.campaign_page.campaigns.all()
        iobjs = InformationObject.objects.filter(
            campaign__in=campaigns,
            foirequest__isnull=False
        ).select_related('foirequest')
        context.update({
            'iobjs': iobjs
        })
        return context


@plugin_pool.register_plugin
class CampaignPlugin(CMSPluginBase):
    module = _("Campaign")
    name = _("Campaign Map")
    render_template = "froide_campaign/plugins/campaign_map.html"
    model = CampaignCMSPlugin
    cache = False

    def get_city_from_request(self, request):
        if GeoIP2 is None:
            return

        ip = get_client_ip(request)
        if not ip:
            logger.warning('No IP found on request: %s', request)
            return
        if ip == '127.0.0.1':
            # Access via localhost
            return

        try:
            g = GeoIP2()
        except Exception as e:
            logger.exception(e)
            return
        try:
            result = g.city(ip)
        except Exception as e:
            logger.exception(e)
            return
        if result and result.get('latitude'):
            return result

    def get_map_config(self, request, instance):
        city = self.get_city_from_request(request)
        campaign_id = instance.campaign.id
        law_type = None

        try:
            law_type = instance.campaign.provider_kwargs.get('law_type')
        except AttributeError:
            pass
        add_location_allowed = instance.campaign.get_provider().CREATE_ALLOWED
        plugin_settings = instance.settings
        request_extra_text = instance.request_extra_text

        has_subscription = False
        if request.user.is_authenticated:
            email = request.user.email
            has_subscription = CampaignSubscription.objects.filter(
                email=email, campaign=instance.campaign).exists()

        plugin_settings.update({
            'city': city or {},
            'campaignId': campaign_id,
            'lawType': law_type,
            'addLocationAllowed': add_location_allowed,
            'requestExtraText': request_extra_text,
            'hasSubscription': has_subscription
        })
        return plugin_settings

    def render(self, context, instance, placeholder):

        context = super().render(context, instance, placeholder)
        request = context.get('request')
        fake_make_request_view = MakeRequestView(request=request)

        context.update({
            'config': json.dumps(self.get_map_config(request, instance)),
            'request_config': json.dumps(
                fake_make_request_view.get_js_context()),
            'request_form': fake_make_request_view.get_form(),
            'user_form': fake_make_request_view.get_user_form()
        })
        return context


@plugin_pool.register_plugin
class CampaignQuestionairePlugin(CMSPluginBase):
    module = _("Campaign")
    name = _("Campaign Questionaire")
    render_template = "froide_campaign/plugins/campaign_questionaire.html"
    model = CampaignQuestionaireCMSPlugin
    cache = False

    def get_questions(self, instance):
        return [{'text': question.text,
                 'id': question.id,
                 'options': question.options.split(','),
                 'required': question.is_required,
                 'helptext': question.help_text
                 }
                for question in instance.questionaire.question_set.all()]

    def get_answers(self, iobj):
        if iobj.report_set.all():
            report = iobj.report_set.all().first()
            answers = report.answer_set.all()
            answer_list = []
            for answer in answers:
                question = answer.question
                answer_dict = {
                    'questionId': question.id,
                    'question': question.text,
                    'options': question.options.split(','),
                    'required': question.is_required,
                    'answer': answer.text,
                    'helptext': question.help_text,
                    'error': ''
                }
                answer_list.append(answer_dict)
            return report.id, answer_list
        return None, []

    def get_iobjs_list(self, instance, iobjs):
        provider = BaseProvider(campaign=instance.questionaire.campaign)
        mapping = provider.get_foirequests_mapping(iobjs)
        data = []
        for obj in iobjs:
            provider_data = provider.get_provider_item_data(
                obj, foirequests=mapping)
            report_id, answers = self.get_answers(obj)
            provider_data['report'] = report_id
            provider_data['answers'] = answers
            data.append(provider_data)

        return data

    def get_list_context(self, context, instance):
        campaign = instance.questionaire.campaign
        iobjs_success = campaign.informationobject_set.filter(
            report__isnull=True,
            foirequests__resolution=Resolution.SUCCESSFUL)
        data = self.get_iobjs_list(instance, iobjs_success)
        context.update({
            'informationobjects': json.dumps(data, cls=DjangoJSONEncoder)
        })
        return context

    def get_object_context(self, context, instance, request_id):
        campaign = instance.questionaire.campaign
        iobjs = campaign.informationobject_set.filter(
            foirequests__resolution=Resolution.SUCCESSFUL
        )
        try:
            foi_request = FoiRequest.objects.get(id=request_id)
            iobjs_request = iobjs.filter(foirequests=foi_request)
            data = self.get_iobjs_list(instance, iobjs_request)
            context.update({
                'informationobjects': json.dumps(data, cls=DjangoJSONEncoder)
            })
            return context

        except FoiRequest.DoesNotExist:
            return self.get_list_context(context, instance)

    def render(self, context, instance, placeholder):
        request = context.get('request')
        context = super().render(context, instance, placeholder)
        config = {
            'viewerUrl': static('filingcabinet/viewer/web/viewer.html')
        }
        context.update({
            'questionaire': instance.questionaire.id,
            'description': instance.questionaire.description,
            'questions': json.dumps(self.get_questions(instance)),
            'config': json.dumps(config),
        })

        request_id = request.GET.get('request_id')
        if request_id:
            return self.get_object_context(context,
                                           instance,
                                           request_id)

        return self.get_list_context(context, instance)


@plugin_pool.register_plugin
class CampaignListPlugin(CMSPluginBase):
    module = _("Campaign")
    name = _("Campaign List")
    render_template = "froide_campaign/plugins/campaign_list.html"
    model = CampaignCMSPlugin
    cache = False

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)
        request = context.get('request')

        lang = get_language()

        campaign = instance.campaign.id
        plugin_settings = instance.settings
        law_type = None
        try:
            law_type = instance.campaign.provider_kwargs.get('law_type')
        except AttributeError:
            pass

        categories = instance.campaign.categories.language(lang)
        categories_dict = [{'id': cat.id, 'title': cat.title}
                           for cat in categories]

        config = {
            'campaignId': campaign,
            'lawType': law_type,
            'categories': categories_dict,
            'requestExtraText': instance.request_extra_text,
        }
        fake_make_request_view = MakeRequestView(request=request)

        context.update({
            'config': json.dumps(config),
            'settings': json.dumps(plugin_settings),
            'request_config': json.dumps(
                fake_make_request_view.get_js_context()),
            'request_form': fake_make_request_view.get_form(),
            'user_form': fake_make_request_view.get_user_form(),
            'language': lang,
        })
        return context


@plugin_pool.register_plugin
class CampaignProgressPlugin(CMSPluginBase):
    module = _("Campaign")
    name = _("Campaign Progress")
    render_template = "froide_campaign/plugins/campaign_progress.html"
    model = CampaignProgressCMSPlugin
    cache = False

    def german_number_display(self, number):
        number = '{0:,}'.format(number)
        return number.replace(",", "X").replace(".", ",").replace("X", ".")

    def get_total(self, instance):
        if not instance.count_featured_only:
            return instance.campaign.get_provider().get_queryset().count()
        else:
            return instance.campaign.informationobject_set.filter(
                featured=True).count()

    def get_requests(self, instance):
        if not instance.count_featured_only:
            return instance.campaign.informationobject_set.filter(
                foirequests__isnull=False).distinct().count()
        else:
            return instance.campaign.informationobject_set.filter(
                featured=True,
                foirequests__isnull=False).distinct().count()

    def get_success(self, instance):
        if not instance.count_featured_only:
            return instance.campaign.informationobject_set.filter(
                foirequests__status='resolved',
                foirequests__resolution='successful').distinct().count()
        else:
            return instance.campaign.informationobject_set.filter(
                featured=True,
                foirequests__status='resolved',
                foirequests__resolution='successful').distinct().count()

    def get_perc(self, amount, total):
        if amount and amount > 0 and total > 0:
            perc = min(int(amount / total * 100), 100)
            return perc
        else:
            return 0

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)
        total = self.get_total(instance)
        requests = self.get_requests(instance)
        success = self.get_success(instance)
        context['amount'] = self.german_number_display(requests)
        context['percentage'] = self.get_perc(requests - success, total)
        context['percentage_success'] = self.get_perc(success, total)
        context['total'] = self.german_number_display(total)
        return context
