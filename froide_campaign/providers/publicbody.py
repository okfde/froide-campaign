from django.template.defaultfilters import slugify

from froide.publicbody.models import PublicBody, Category, Classification
from froide.georegion.models import GeoRegion

from ..models import InformationObject

from .base import BaseProvider, first


class PublicBodyProvider(BaseProvider):
    def get_queryset(self):
        qs = PublicBody.objects.all()
        filters = {}
        tree_filter = (
            ('categories', Category),
            ('classification', Classification),
            ('regions', GeoRegion)
        )

        for key, model in tree_filter:
            if key not in self.kwargs:
                continue
            try:
                obj = model.objects.get(id=self.kwargs[key])
            except model.DoesNotExist:
                continue
            filters[key + '__in'] = model.get_tree(obj)

        attr_filters = (
            'jurisdiction_id',
        )
        for key, model in attr_filters:
            if key not in self.kwargs:
                continue
            filters[key] = self.kwargs[key]

        return qs.filter(
            **filters
        )

    def filter(self, qs, **filter_kwargs):
        if filter_kwargs.get('q'):
            qs = qs.filter(name__contains=filter_kwargs['q'])
        return qs

    def get_ident_list(self, qs):
        return [
            obj.id for obj in qs
        ]

    def get_by_ident(self, ident):
        return self.get_queryset().get(id=ident)

    def get_provider_item_data(self, obj, foirequests=None, detail=False):
        d = {
            'ident': obj.id,
            'request_url': self.get_request_url_redirect(obj.id),
            'title': obj.name,
            'description': '',
            'lat': obj.geo.y if obj.geo else None,
            'lng': obj.geo.x if obj.geo else None,
            'foirequests': foirequests,
        }

        if foirequests:
            d.update({
                'foirequest': first(foirequests[obj.id]),
                'foirequests': foirequests[obj.id]
            })
        return d

    def get_request_url_context(self, obj):
        return {
            'title': obj.name,
            'address': obj.address,
            'contact': obj.contact,
            'publicbody': obj
        }

    def get_request_url_with_object(self, ident, obj):
        context = self.get_request_url_context(obj)
        return self.make_request_url(ident, context, obj)

    def connect_request(self, ident, sender):
        if not sender.public:
            return

        try:
            pb = self.get_by_ident(ident)
        except PublicBody.DoesNotExist:
            return

        context = self.get_request_url_context(pb)

        iobj, created = InformationObject.objects.get_or_create(
            campaign=self.campaign,
            ident=ident,
            defaults=dict(
                title=context['title'],
                slug=slugify(context['title']),
                publicbody=sender.public_body,
                geo=pb.geo,
                foirequest=sender
            )
        )

        iobj.foirequests.add(sender)
