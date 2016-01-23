# -*- encoding: utf-8 -*-
from django.apps import AppConfig


class FroideCampaignConfig(AppConfig):
    name = 'froide_campaign'
    verbose_name = "Froide Campaign App"

    def ready(self):
        from .listeners import connect_info_object

        from froide.foirequest.models import FoiRequest
        FoiRequest.request_created.connect(connect_info_object)
