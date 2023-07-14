from django.db.models import Prefetch

from froide.campaign.utils import connect_foirequest
from froide.foirequest.models import FoiRequest

from ..filters import (
    CategoryFilter,
    FeaturedFilter,
    GeoDistanceFilter,
    InformationObjectRequestedFilter,
    InformationObjectSearchVectorFilter,
    RandomOrderFilter,
    StatusFilter,
)
from ..models import InformationObject
from ..serializers import CampaignProviderItemSerializer
from .base import BaseProvider


class InformationObjectProvider(BaseProvider):
    filter_backends = [
        InformationObjectSearchVectorFilter,
        StatusFilter,
        CategoryFilter,
        FeaturedFilter,
        GeoDistanceFilter,
        InformationObjectRequestedFilter,
        RandomOrderFilter,
    ]
    ORDER_BY = "-featured"
    # search_fields = ["translations__title", "translations__subtitle"]

    def make_ident(self, obj: InformationObject):
        return obj.ident

    def get_by_ident(self, ident):
        return InformationObject.objects.get(campaign=self.campaign, ident=ident)

    def get_queryset(self):
        iobjs = InformationObject.objects.filter(campaign=self.campaign).select_related(
            "publicbody"
        )
        iobjs = iobjs.prefetch_related(
            Prefetch("foirequests", queryset=FoiRequest.objects.order_by("-created_at"))
        )
        iobjs = iobjs.prefetch_related("campaign")
        iobjs = iobjs.prefetch_related("categories")
        return iobjs

    def detail(self, ident):
        obj = self.get_by_ident(ident)
        data = self.get_provider_item_data(obj, detail=True)
        serializer = CampaignProviderItemSerializer(data)
        return serializer.data

    def get_provider_item_data(self, obj, foirequests=None, detail=False):
        pb = self.get_publicbody(obj)
        data = {
            "id": obj.id,
            "ident": obj.ident,
            "title": obj.title,
            "subtitle": obj.subtitle,
            "address": obj.address,
            "request_url": self.get_request_url_redirect(obj.ident),
            "publicbody_name": pb.name if pb else None,
            "description": obj.get_description(),
            "lat": obj.get_latitude(),
            "lng": obj.get_longitude(),
            "foirequest": None,
            "foirequests": [],
            "resolution": "normal",
            "context": obj.context,
            # obj.categories + translations prefetched
            "categories": [
                {"id": c.id, "title": c.title} for c in obj.categories.all()
            ],
            "featured": obj.featured,
        }

        if foirequests and foirequests[obj.ident]:
            data.update(self.get_foirequest_api_data(foirequests[obj.ident]))

        return data

    def get_publicbodies(self, obj):
        if obj.publicbody:
            return [obj.publicbody]
        return []

    def get_request_url_context(self, obj, language=None):
        return obj.get_context(language)

    def connect_request(self, ident, sender):
        try:
            iobj = self.get_by_ident(ident)
        except InformationObject.DoesNotExist:
            return

        if iobj.publicbody != sender.public_body:
            return

        if iobj.foirequest is None:
            iobj.foirequest = sender

        iobj.foirequests.add(sender)
        iobj.save()

        connect_foirequest(sender, self.campaign.slug)

        return iobj
