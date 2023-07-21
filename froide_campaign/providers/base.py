import html
from collections import defaultdict
from typing import Any, Dict, List, Optional, Protocol
from urllib.parse import quote, urlencode

from django.conf import settings
from django.template import Context
from django.urls import reverse

from froide.foirequest.auth import get_read_foirequest_queryset
from froide.foirequest.models import FoiRequest
from froide.publicbody.models import PublicBody

from ..models import InformationObject
from ..serializers import (
    CampaignProviderItemSerializer,
    CampaignProviderRequestSerializer,
)

LIMIT = 100


class ProviderProtocol(Protocol):
    def __init__(self, campaign, **kwargs):
        ...

    def get_queryset(self):
        ...

    def get_serializer(self, obj_or_list, **kwargs):
        ...

    def get_item_data(self, obj: Any, foirequests=None, detail=False) -> Dict[str, Any]:
        ...

    def make_ident(self, obj: Any) -> str:
        ...

    def get_request_url_context(
        self, obj: Any, language=Optional[str]
    ) -> Dict[str, Any]:
        ...

    def get_publicbodies(self, obj: Any) -> List[PublicBody]:
        ...


def first(x):
    if not x:
        return
    return None


class BaseProvider:
    ORDER_ZOOM_LEVEL = 15
    filter_backends = []

    def __init__(self, campaign, **kwargs):
        self.campaign = campaign
        self.kwargs = kwargs

    def search(self, request, queryset):
        return self.filter_queryset(request, queryset)

    def filter_queryset(self, request, queryset):
        """
        Given a queryset, filter it with whichever filter backend is in use.

        You are unlikely to want to override this method, although you may need
        to call it either from a list view, or from a custom `get_object`
        method if you want to apply the configured filtering backend to the
        default queryset.
        """
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(request, queryset, self)
        return queryset

    def get_ident_list(self, qs):
        return [self.make_ident(obj) for obj in qs]

    def get_foirequests_mapping(self, qs, request=None):
        ident_list = self.get_ident_list(qs)
        iobjs = InformationObject.objects.filter(
            ident__in=ident_list, campaign=self.campaign
        )
        mapping = defaultdict(list)

        through_qs = InformationObject.foirequests.through.objects.filter(
            informationobject__in=iobjs
        )

        readable_private_requests = set()
        if request is not None:
            readable_private_requests = set(
                get_read_foirequest_queryset(
                    request,
                    FoiRequest.objects.filter(
                        id__in=through_qs.filter(
                            foirequest__visibility=FoiRequest.VISIBILITY.VISIBLE_TO_REQUESTER
                        ).values_list("foirequest_id", flat=True)
                    ),
                ).values_list("id", flat=True)
            )

        iterable = through_qs.order_by("-foirequest__created_at").values_list(
            "informationobject__ident",
            "foirequest_id",
            "foirequest__resolution",
            "foirequest__visibility",
        )

        for iobj_ident, fr_id, resolution, visibility in iterable:
            is_public = visibility == FoiRequest.VISIBILITY.VISIBLE_TO_PUBLIC
            mapping[iobj_ident].append(
                {
                    "id": fr_id,
                    "resolution": resolution,
                    "public": is_public,
                    "readable": is_public or fr_id in readable_private_requests,
                }
            )

        return mapping

    def make_request_url(self, ident, context, publicbody=None):
        if publicbody is not None:
            pb_slug = publicbody.slug
            url = reverse(
                "foirequest-make_request", kwargs={"publicbody_slug": pb_slug}
            )
        else:
            url = reverse("foirequest-make_request")
        context = Context(context)
        subject = html.unescape(self.campaign.get_subject_template().render(context))
        if len(subject) > 250:
            subject = subject[:250] + "..."
        body = html.unescape(self.campaign.get_template().render(context)).encode(
            "utf-8"
        )
        ref = ("campaign:%s@%s" % (self.campaign.pk, ident)).encode("utf-8")
        query = {"subject": subject.encode("utf-8"), "body": body, "ref": ref}
        if self.kwargs.get("lawType"):
            query["law_type"] = self.kwargs["lawType"].encode()

        if self.kwargs.get("redirect_url"):
            query["redirect_url"] = self.kwargs["redirect_url"].encode()

        hide_features = ["public", "full_text", "similar", "draft", "editing"]
        if publicbody is not None:
            hide_features.append("publicbody")

        hide_features = [
            "hide_{}".format(x)
            for x in hide_features
            if not self.kwargs.get("show_{}".format(x))
        ]

        query.update({f: b"1" for f in hide_features})
        query = urlencode(query, quote_via=quote)
        return "%s%s?%s" % (settings.SITE_URL, url, query)

    def get_user_request_count(self, user):
        if not user.is_authenticated:
            return 0
        return InformationObject.objects.filter(
            campaign=self.campaign, foirequests__user=user
        ).count()

    def get_request_url_redirect(self, ident):
        return reverse(
            "campaign-redirect_to_make_request",
            kwargs={"campaign_id": self.campaign.id, "ident": ident},
        )

    def get_request_url(self, obj, publicbody=None, language=None):
        context = self.get_request_url_context(obj, language=language)
        if publicbody is None:
            publicbody = self.get_publicbody(obj)
        ident = self.make_ident(obj)
        return self.make_request_url(ident, context, publicbody)

    def get_serializer(self, obj_or_list, many=False, **kwargs):
        if not many:
            obj_or_list = [obj_or_list]

        foirequests_mapping = self.get_foirequests_mapping(
            obj_or_list, request=kwargs.get("context", {}).get("request")
        )

        data = [
            self.get_item_data(pb, foirequests=foirequests_mapping)
            for pb in obj_or_list
        ]
        if not many:
            data = data[0]

        return CampaignProviderItemSerializer(data, many=many, **kwargs)

    def get_detail_data(self, obj):
        serializer = self.get_serializer(obj, many=False)
        return serializer.data

    def get_foirequest_api_data(self, frs):
        fr_id, res = frs[0].get("id"), frs[0].get("resolution")
        public = frs[0].get("public", False)
        readable = frs[0].get("readable", False)

        success_strings = ["successful", "partially_successful"]
        withdrawn_strings = ["user_withdrew_costs", "user_withdrew"]

        resolution = "pending"
        if res:
            if res in success_strings:
                resolution = "successful"
            if res == "refused":
                resolution = "refused"
            if res in withdrawn_strings:
                resolution = "user_withdrew"

        return {
            "foirequest": fr_id,
            "foirequests": frs,
            "resolution": resolution,
            "public": public,
            "readable": readable,
        }

    def get_request_serializer(self, request, ident, language=None):
        obj = self.get_by_ident(ident)
        if isinstance(obj, InformationObject):
            data = self.get_default_item_data(obj, detail=True)
            pbs = self.get_default_publicbodies(obj)
        else:
            data = self.get_item_data(obj, detail=True)
            pbs = self.get_publicbodies(obj)
        pb = pbs[0] if pbs else None
        data["publicbody"] = pb
        data["publicbodies"] = pbs
        data["makeRequestURL"] = self.get_request_url(
            obj, publicbody=pb, language=language
        )
        data["userRequestCount"] = self.get_user_request_count(request.user)
        return CampaignProviderRequestSerializer(data, context={"request": request})

    def get_default_publicbodies(self, obj):
        if obj.publicbody:
            return [obj.publicbody]
        return []

    def get_publicbody(self, obj) -> Optional[PublicBody]:
        pbs = self.get_publicbodies(obj)
        if len(pbs) == 0:
            return None
        return pbs[0]

    def can_add_items(self, request):
        return False

    def get_default_item_data(self, obj, foirequests=None, detail=False):
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
