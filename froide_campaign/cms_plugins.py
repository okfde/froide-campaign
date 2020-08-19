import json
import logging

from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.urls import reverse

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from .models import (CampaignRequestsCMSPlugin,
                     InformationObject,
                     CampaignCMSPlugin)

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

    def get_city_from_request(self, request):
        if GeoIP2 is None:
            return

        ip = get_client_ip(request)
        if not ip:
            logger.warning('No IP found on request: %s', request)
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

        return {
            'city': city or {},
            'campaignId': instance.campaign.id
        }

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)
        iobjs = InformationObject.objects.filter(
            campaign=instance.campaign
        ).select_related('foirequest')

        request = context.get('request')

        context.update({
            'iobjs': iobjs,
            'config': json.dumps(self.get_map_config(request, instance))
        })
        return context
