import operator
from functools import reduce

from django.db.models import Q
from django.template.defaultfilters import slugify

from django_amenities.models import Amenity
from rest_framework import filters

from froide.campaign.utils import connect_foirequest
from froide.georegion.models import GeoRegion
from froide.publicbody.models import PublicBody

from ..filters import GeoDistanceFilter
from ..models import InformationObject
from .base import BaseProvider


class AmenitySearchFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        q = request.GET.get("q")
        if q:
            return queryset.filter(name__icontains=q)
        return queryset


class AmenityProvider(BaseProvider):
    # TODO Needs to be fixed for new protocol from base
    CREATE_ALLOWED = True
    ADMIN_LEVELS = ["borough", "municipality", "admin_cooperation", "district", "state"]
    ORDER_BY = "id"
    filter_backends = [
        AmenitySearchFilter,
        GeoDistanceFilter,
        # StatusFilter,
        # InformationObjectRequestedFilter,
    ]

    def get_queryset(self):
        # iobjs = InformationObject.objects.filter(campaign=self.campaign)
        # ident_list = iobjs.values_list("ident", flat=True)
        # osm_ids = [
        #     int(ident.split("_")[1]) for ident in ident_list if "custom" not in ident
        # ]

        amenities = Amenity.objects.filter(
            topics__contains=[self.kwargs.get("amenity_topic", "")]
        ).exclude(name="")

        if self.kwargs.get("exclude"):
            clauses = (Q(name__icontains=p) for p in self.kwargs.get("exclude"))
            query = reduce(operator.or_, clauses)
            amenities = amenities.exclude(query)

        return amenities

    def make_ident(self, obj: Amenity) -> str:
        return obj.ident

    def get_by_ident(self, ident: str) -> Amenity:
        pk = ident.split("_")[0]
        return self.get_queryset().get(id=pk)

    def get_provider_item_data(self, obj: Amenity, foirequests=None, detail=False):
        data = {
            "id": obj.id,
            "ident": obj.ident,
            "request_url": self.get_request_url_redirect(obj.ident),
            "title": obj.name,
            "address": obj.address,
            "description": "",
            "lat": obj.geo.y,
            "lng": obj.geo.x,
            "resolution": "normal",
            "foirequest": None,
            "foirequests": [],
        }

        if foirequests and foirequests[obj.ident]:
            data.update(self.get_foirequest_api_data(foirequests[obj.ident]))

        return data

    def get_publicbodies(self, amenity: Amenity):
        pbs = PublicBody.objects.all()

        regions = (
            GeoRegion.objects.filter(
                geom__covers=amenity.geo,
            )
            .filter(kind__in=self.ADMIN_LEVELS)
            .order_by("kind")
        )

        pbs = pbs.filter(regions__in=regions)

        cats = []
        if self.kwargs.get("categories"):
            cats = self.kwargs["categories"]
        elif self.kwargs.get("category"):
            cats = [self.kwargs["category"]]

        for cat in cats:
            cat_pbs = pbs.filter(
                categories__name=cat,
            )
            if cat_pbs:
                return cat_pbs
        return pbs

    def get_request_url_context(self, obj: Amenity, language=None):
        return {"title": obj.name, "address": obj.address, "amenity": obj}

    def connect_request(self, ident, sender):
        try:
            amenity = self.get_by_ident(ident)
        except Amenity.DoesNotExist:
            return

        context = self.get_request_url_context(amenity, language=None)

        iobj, created = InformationObject.objects.get_or_create(
            campaign=self.campaign,
            ident=ident,
            defaults=dict(
                title=context["title"],
                slug=slugify(context["title"]),
                publicbody=sender.public_body,
                geo=amenity.geo,
                foirequest=sender,
            ),
        )

        if created:
            qs = InformationObject.objects.filter(id=iobj.id)
            InformationObject.objects.update_search_index(qs=qs)

        if not created:
            iobj.publicbody = sender.public_body
            iobj.save()

        connect_foirequest(sender, self.campaign.slug)

        iobj.foirequests.add(sender)

        return iobj
