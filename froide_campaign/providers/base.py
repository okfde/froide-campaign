from collections import defaultdict
from urllib.parse import urlencode

from django.urls import reverse
from django.conf import settings
from django.template import Context
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance

from ..models import InformationObject
from .serializers import CampaignProviderItemSerializer


LIMIT = 50


def first(x):
    if not x:
        return
    return None


class BaseProvider:
    ORDER_ZOOM_LEVEL = 15

    def __init__(self, campaign, **kwargs):
        self.campaign = campaign
        self.kwargs = kwargs

    def get_by_ident(self, ident):
        return InformationObject.objects.get(
            campaign=self.campaign,
            ident=ident
        )

    def get_ident_list(self, qs):
        return [
            i.ident for i in qs
        ]

    def get_queryset(self):
        return InformationObject.objects.filter(
            campaign=self.campaign
        ).select_related('publicbody')

    def search(self, **filter_kwargs):
        iobjs = self.get_queryset()
        iobjs = self.filter(iobjs, **filter_kwargs)
        iobjs = self.filter_geo(iobjs, **filter_kwargs)
        iobjs = self.limit(iobjs)

        foirequests_mapping = self.get_foirequests_mapping(iobjs)

        data = [
            self.get_provider_item_data(iobj, foirequests=foirequests_mapping)
            for iobj in iobjs
        ]

        serializer = CampaignProviderItemSerializer(
            data, many=True
        )
        return serializer.data

    def detail(self, ident):
        obj = self.get_by_ident(ident)
        data = self.get_provider_item_data(obj, detail=True)
        serializer = CampaignProviderItemSerializer(data)
        return serializer.data

    def filter(self, iobjs, **filter_kwargs):
        if filter_kwargs.get('q'):
            iobjs = InformationObject.objects.search(
                iobjs, filter_kwargs['q']
            )
        if filter_kwargs.get('requested'):
            iobjs = iobjs.filter(
                foirequests__isnull=False
            )
        return iobjs

    def filter_geo(self, qs, q=None, coordinates=None, radius=None, zoom=None, **kwargs):
        if coordinates is None:
            return qs

        if radius is None:
            radius = 1000
        radius = int(radius * 0.9)

        qs = (
            qs.filter(geo__isnull=False)
            .filter(geo__dwithin=(coordinates, radius))
            .filter(
                geo__distance_lte=(coordinates, D(m=radius))
            )
        )
        order_distance = zoom is None or zoom >= self.ORDER_ZOOM_LEVEL
        if not q and order_distance:
            qs = (
                qs.annotate(distance=Distance("geo", coordinates))
                .order_by("distance")
            )
        else:
            qs = qs.order_by('?')

        return qs

    def limit(self, qs):
        return qs[:self.kwargs.get('limit', LIMIT)]

    def get_provider_item_data(self, obj, foirequests=None, detail=False):
        d = {
            'ident': obj.ident,
            'title': obj.title,
            'request_url': self.get_request_url_redirect(obj.ident),
            'publicbody_name': self.get_publicbody_name(obj),
            'description': obj.get_description(),
            'lat': obj.get_latitude,
            'lng': obj.get_longitude,
        }
        if foirequests:
            d.update({
                'foirequest': first(foirequests[obj.id]),
                'foirequests': foirequests[obj.id]
            })
        return d

    def get_foirequests_mapping(self, qs):
        ident_list = self.get_ident_list(qs)
        iobjs = InformationObject.objects.filter(
            ident__in=ident_list
        )
        mapping = defaultdict(list)

        iterable = InformationObject.foirequests.through.objects.filter(
                informationobject__in=iobjs
            ).values_list('informationobject_id', 'foirequest_id')
        for iobj_id, fr_id in iterable:
            mapping[iobj_id].append(fr_id)

        return mapping

    def get_publicbody_name(self, obj):
        if obj.publicbody is None:
            return ''
        return obj.publicbody.name

    def get_publicbody(self, ident):
        obj = self.get_by_ident(ident)
        return self._get_publicbody(obj)

    def get_request_url_redirect(self, ident):
        return reverse('campaign-redirect_to_make_request', kwargs={
            'campaign_id': self.campaign.id,
            'ident': ident
        })

    def get_request_url(self, ident):
        obj = self.get_by_ident(ident)
        return self.get_request_url_with_object(ident, obj)

    def get_request_url_context(self, obj):
        return obj.get_context()

    def get_request_url_with_object(self, ident, obj):
        context = self.get_request_url_context(obj)
        publicbody = self._get_publicbody(obj)
        return self.make_request_url(ident, context, publicbody)

    def make_request_url(self, ident, context, publicbody):
        pb_slug = publicbody.slug
        url = reverse('foirequest-make_request', kwargs={
            'publicbody_slug': pb_slug
        })
        context = Context(context)
        subject = self.campaign.get_subject_template().render(context)
        if len(subject) > 250:
            subject = subject[:250] + '...'
        body = self.campaign.get_template().render(context).encode('utf-8')
        ref = ('campaign:%s@%s' % (self.campaign.pk, ident)).encode('utf-8')
        query = {
            'subject': subject.encode('utf-8'),
            'body': body,
            'ref': ref
        }
        hide_features = (
            'hide_public', 'hide_full_text', 'hide_similar', 'hide_publicbody',
            'hide_draft', 'hide_editing'
        )
        query.update({f: b'1' for f in hide_features})
        query = urlencode(query)
        return '%s%s?%s' % (settings.SITE_URL, url, query)
