from typing import Optional

from django.template import Context
from django.template.defaultfilters import slugify
from django.utils.safestring import mark_safe

from froide.campaign.utils import connect_foirequest
from froide.georegion.models import GeoRegion
from froide.publicbody.models import Category, Classification, PublicBody

from ..models import InformationObject
from .base import BaseProvider


class PublicBodyProvider(BaseProvider):
    IDENT_PREFIX = "pb-"

    def get_queryset(self):
        qs = PublicBody.objects.all()
        filters = {}
        tree_filter = (
            ("category", "categories", Category),
            ("classification", "classification", Classification),
            ("region", "regions", GeoRegion),
        )

        for key, field, model in tree_filter:
            if key not in self.kwargs:
                continue
            try:
                obj = model.objects.get(id=self.kwargs[key])
            except model.DoesNotExist:
                continue
            filters[field + "__in"] = model.get_tree(obj)

        attr_filters = (
            (
                "jurisdiction",
                "jurisdiction_id",
            ),
        )
        for key, field in attr_filters:
            if key not in self.kwargs:
                continue
            filters[field] = self.kwargs[key]

        return qs.filter(**filters)

    def make_ident(self, obj: PublicBody):
        return "{}{}".format(self.IDENT_PREFIX, obj.id)

    def get_by_ident(self, ident: str) -> Optional[PublicBody]:
        try:
            obj_id = int(ident.split(self.IDENT_PREFIX)[-1])
        except ValueError:
            return None
        return self.get_queryset().filter(id=obj_id).first()

    def get_description(self, obj: PublicBody):
        template = self.campaign.get_description_template()
        context = Context(self.get_request_url_context(obj))
        return mark_safe(template.render(context))

    def get_provider_item_data(self, obj: PublicBody, foirequests=None):
        ident = self.make_ident(obj)
        data = {
            "id": obj.id,
            "ident": ident,
            "request_url": self.get_request_url_redirect(ident),
            "title": obj.name,
            "description": self.get_description(obj),
            "publicbody_name": obj.name,
            "lat": obj.geo.y if obj.geo else None,
            "lng": obj.geo.x if obj.geo else None,
            "foirequest": None,
            "foirequests": [],
            "resolution": "normal",
        }

        if foirequests and foirequests[ident]:
            data.update(self.get_foirequest_api_data(foirequests[ident]))

        return data

    def get_request_url_context(self, obj: PublicBody, language=None):
        return {
            "title": obj.name,
            "address": obj.address,
            "contact": obj.contact,
            "publicbody": obj,
        }

    def connect_request(self, ident: str, sender):
        try:
            pb = self.get_by_ident(ident)
        except PublicBody.DoesNotExist:
            return

        context = self.get_request_url_context(pb)

        iobj, created = InformationObject.objects.get_or_create(
            campaign=self.campaign,
            ident=ident,
            defaults=dict(
                title=context["title"],
                slug=slugify(context["title"]),
                publicbody=sender.public_body,
                geo=pb.geo,
                foirequest=sender,
            ),
        )

        iobj.foirequests.add(sender)

        connect_foirequest(sender, self.campaign.slug)

        return pb

    def get_publicbodies(self, obj: PublicBody):
        return [obj]
