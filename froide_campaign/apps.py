import json

from django.apps import AppConfig
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


class FroideCampaignConfig(AppConfig):
    name = 'froide_campaign'
    verbose_name = _("Froide Campaign App")

    def ready(self):
        from .listeners import connect_info_object

        from froide.foirequest.models import FoiRequest
        FoiRequest.request_created.connect(connect_info_object)

        from froide.account.menu import menu_registry, MenuItem
        from froide.account.export import registry
        from froide.account import account_merged

        registry.register(export_user_data)
        account_merged.connect(merge_user)

        @menu_registry.register
        def get_campaign_menu_item(request):
            if not request.user.has_perm('froide_campaign.can_use_campaigns'):
                return None
            return MenuItem(
                section='before_settings', order=10,
                url=reverse('campaign-list'),
                label=_('My campaigns')
            )


def merge_user(sender, old_user=None, new_user=None, **kwargs):
    from froide.account.utils import move_ownership
    from .models import CampaignPage

    move_ownership(CampaignPage, 'user', old_user, new_user)


def export_user_data(user):
    from froide.foirequest.models.request import get_absolute_domain_short_url
    from .models import CampaignPage, InformationObject

    campaign_pages = (
        CampaignPage.objects
        .filter(user=user)
    )
    if campaign_pages:
        yield ('campaign_pages.json', json.dumps([
            {
                'title': p.title,
                'slug': p.slug,
                'team_id': p.team_id,
                'settings': p.settings,
                'embed': p.get_absolute_domain_embed_url(),
                'public': p.public,
                'description': p.description,
                'campaigns': [c.id for c in p.campaigns.all()]
            }
            for p in campaign_pages]).encode('utf-8')
        )

    iobjs = InformationObject.objects.filter(
        foirequest__user=user
    ).select_related('campaign')
    if iobjs:
        yield ('campaign_requests.json', json.dumps([
            {
                'campaign': i.campaign.title,
                'ident': i.ident,
                'title': i.title,
                'slug': i.slug,
                'ordering': i.ordering,
                'context': i.context,
                'request': (
                    get_absolute_domain_short_url(i.foirequest_id)
                    if i.foirequest_id else None
                ),
                'resolved': i.resolved,
                'resolution_text': i.resolution_text,
                'resolution_link': i.resolution_link,
            }
            for i in iobjs]).encode('utf-8')
        )
