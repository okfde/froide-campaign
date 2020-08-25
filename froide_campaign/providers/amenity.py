from django_amenities.models import Amenity

from froide.publicbody.models import PublicBody
from froide.georegion.models import GeoRegion

from .base import BaseProvider, first


class AmenityProvider(BaseProvider):
    def get_queryset(self):
        return Amenity.objects.filter(
            topics__contains=[self.kwargs.get('amenity_topic', '')],
        ).exclude(name='')

    def get_ident_list(self, qs):
        return [
            obj.ident for obj in qs
        ]

    def filter(self, qs, **filter_kwargs):
        if filter_kwargs.get('q'):
            qs = qs.filter(name__contains=filter_kwargs['q'])
        return qs

    def get_by_ident(self, ident):
        pk = ident.split('_')[0]
        return self.get_queryset().get(id=pk)

    def get_provider_item_data(self, obj, foirequests=None, detail=False):
        d = {
            'ident': obj.ident,
            'request_url': self.get_request_url_redirect(obj.ident),
            'title': obj.name,
            'description': '',
            'lat': obj.geo.y,
            'lng': obj.geo.x,
            'foirequests': foirequests,
        }

        if foirequests:
            d.update({
                'foirequest': first(foirequests[obj.id]),
                'foirequests': foirequests[obj.id]
            })
        return d

    def _get_publicbody(self, amenity):
        pbs = PublicBody.objects.all()
        if self.kwargs.get('category'):
            pbs = pbs.filter(
                categories__name=self.kwargs['category'],
            )

        regions = GeoRegion.objects.filter(
            geom__covers=amenity.geo,
        ).exclude(
            kind__in=['country', 'zipcode']
        ).order_by('kind')

        pbs = pbs.filter(
            regions__in=regions
        )
        if len(pbs) == 0:
            return None
        elif len(pbs) > 1:
            return pbs[0]
        return pbs[0]

    def get_request_url_context(self, obj):
        return {
            'title': obj.name,
            'address': obj.address
        }
