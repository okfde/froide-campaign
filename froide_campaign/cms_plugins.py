from django.utils.translation import gettext_lazy as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from .models import CampaignRequestsCMSPlugin, InformationObject


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
