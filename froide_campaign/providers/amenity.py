import operator
from collections import namedtuple
from functools import reduce

from django.db.models import CharField, F, Q, Value
from django.db.models.functions import Concat, Trim
from django.template.defaultfilters import slugify

from django_amenities.models import Amenity
from rest_framework import filters

from froide.campaign.utils import connect_foirequest
from froide.georegion.models import GeoRegion
from froide.publicbody.models import PublicBody

from ..filters import GeoDistanceFilter
from ..models import InformationObject
from .base import BaseProvider
from .informationobject import InformationObjectProvider

VALUES_LIST = ("id_", "ident_", "title_", "address_", "geo_")
InformationObjectLike = namedtuple(
    "InformationObjectLike", ("id", "ident", "title", "address", "geo")
)


class InformationObjectRequestedFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, provider):
        if request.GET.get("requested") is not None:
            try:
                is_requested = bool(request.GET["requested"])
                requested_iobjs = InformationObject.objects.filter(
                    campaign=provider.campaign,
                    foirequests__isnull=not is_requested,
                ).values_list("publicbody_id", flat=True)
                queryset = queryset.filter(id__in=requested_iobjs)
            except ValueError:
                pass
        return queryset


class StatusFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, provider):
        if request.GET.get("status"):
            iobjs = InformationObject.objects.filter(campaign=provider.campaign)
            status = request.GET.get("status")
            if status == "normal":
                iobjs = iobjs.filter(foirequests__isnull=False)
                return queryset.exclude(
                    id__in=iobjs.values_list("publicbody_id", flat=True)
                )
            if status == "pending":
                iobjs = iobjs.filter(foirequests__isnull=False).exclude(
                    foirequests__status="resolved"
                )
            if status == "successful":
                successful = ["successful", "partially_successful"]
                iobjs = iobjs.filter(
                    foirequests__status="resolved",
                    foirequests__resolution__in=successful,
                )
            if status == "refused":
                iobjs = iobjs.filter(
                    foirequests__status="resolved", foirequests__resolution="refused"
                )
            return queryset.filter(id__in=iobjs.values_list("publicbody_id", flat=True))
        return queryset


class AmenitySearchFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        q = request.GET.get("q")
        if q:
            return queryset.filter(name__icontains=q)
        return queryset


class AmenityProvider(BaseProvider):
    ADMIN_LEVELS = ["borough", "municipality", "admin_cooperation", "district", "state"]
    ORDER_BY = "id"
    filter_backends = [
        AmenitySearchFilter,
        GeoDistanceFilter,
        StatusFilter,
        InformationObjectRequestedFilter,
    ]

    def can_add_items(self, request):
        return False

    def get_queryset(self):
        amenities = Amenity.objects.filter(
            topics__contains=[self.kwargs.get("amenity_topic", "")]
        ).exclude(name="")

        if self.kwargs.get("exclude"):
            clauses = (Q(name__icontains=p) for p in self.kwargs.get("exclude"))
            query = reduce(operator.or_, clauses)
            amenities = amenities.exclude(query)

        return amenities

    def search(self, request, queryset):
        """
        Why is this so complicated?
        Because UNIONs expect same field order.
        But we need to .annotate() some fields and that makes the order weird,
        even when using values_list and that breaks UNION.
        So we annotate all fields on both models that we need
        and then values_list them, then union, then order by geo distance
        and then values_list again to get named tuples.
        """
        amenity_qs = self.filter_queryset(request, queryset)
        amenity_qs = amenity_qs.annotate(
            id_=F("id"),
            ident_=Concat("id", Value("_"), "osm_id", output_field=CharField()),
            title_=F("name"),
            address_=Trim(
                Concat(
                    Trim(
                        Concat(
                            "street",
                            Value(" "),
                            "housenumber",
                            output_field=CharField(),
                        )
                    ),
                    Value("\n"),
                    Trim(
                        Concat(
                            "postcode", Value(" "), "city", output_field=CharField()
                        ),
                    ),
                    output_field=CharField(),
                )
            ),
            geo_=F("geo"),
        ).values_list(*VALUES_LIST, named=True)
        # Clear ordering
        amenity_qs = amenity_qs.order_by()

        iobj_provider = InformationObjectProvider(self.campaign)
        iobj_qs = iobj_provider.get_queryset().filter(ident__startswith="custom_")
        iobj_qs = iobj_provider.search(request, iobj_qs)
        iobj_qs = iobj_qs.annotate(
            id_=F("id"),
            ident_=F("ident"),
            title_=F("translations__title"),
            address_=F("address"),
            geo_=F("geo"),
        )
        iobj_qs = iobj_qs.values_list(*VALUES_LIST, named=True)
        # Clear any order bys
        iobj_qs = iobj_qs.order_by()
        qs = amenity_qs.union(iobj_qs, all=True)
        # Skip ordering, it's too expensive
        # Instead if the geobox filters amenity qs to a small enough set
        # it can't get topped up by iobj qs

        return qs.values_list(*VALUES_LIST, named=True)

    def get_serializer(self, obj_or_list, many=False, **kwargs):
        if many:
            obj_or_list = [InformationObjectLike._make(o) for o in obj_or_list]
        else:
            obj_or_list = InformationObjectLike(
                id=obj_or_list.id,
                ident=obj_or_list.ident,
                title=obj_or_list.title,
                address=obj_or_list.address,
                geo=obj_or_list.geo,
            )
        return super().get_serializer(obj_or_list, many, **kwargs)

    def make_ident(self, obj) -> str:
        return obj.ident

    def get_by_ident(self, ident: str) -> Amenity:
        pk, rest = ident.split("_", 1)
        if pk == "custom":
            return InformationObject.objects.get(ident=ident)
        qs = self.get_queryset()
        qs = qs.annotate(title=F("name"))
        return qs.get(id=pk)

    def get_item_data(self, obj: InformationObjectLike, foirequests=None, detail=False):
        data = {
            "id": obj.id,
            "ident": obj.ident,
            "request_url": self.get_request_url_redirect(obj.ident),
            "title": obj.title,
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
