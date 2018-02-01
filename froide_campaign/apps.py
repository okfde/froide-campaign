# -*- encoding: utf-8 -*-
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

        @menu_registry.register
        def get_campaign_menu_item(request):
            if not request.user.has_perm('froide_campaign.can_use_campaigns'):
                return None
            return MenuItem(
                section='before_settings', order=10,
                url=reverse('campaign-list'),
                label=_('Your campaigns')
            )
