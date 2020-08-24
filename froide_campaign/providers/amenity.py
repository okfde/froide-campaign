from django_amenities.models import Amenity

from froide.publicbody.models import PublicBody
from froide.georegion.models import GeoRegion

from .base import BaseProvider


class AmenityProvider(BaseProvider):
    def get_queryset(self):
        return Amenity.objects.filter(
            topics__contains=[self.kwargs.get('amenity_topic', '')],
        ).exclude(name='')

    def search(self, *args, **kwargs):        
        qs = self.get_queryset()

        # TODO: point radius    
        # .filter(geo__dwithin=(point, radius))
        # .filter(geo__distance_lte=(point, D(m=radius)))

        qs = self.limit(qs)

        data = [{
            'title': a.name,
            'description': '',
            'lat': a.geo.y,
            'lng': a.geo.x
            'publicbody': self.get_publicbody(a.osm_id)
        } for a in qs]

        serializer = InformationObjectSerializer(
            data, many=True
        )
        return serializer.data

    def _get_amenity(self, ident):
        return Amenity.objects.get(osm_id=ident)

    def get_publicbody(self, ident):
        amenity = self._get_amenity(ident)
        pbs = PublicBody.objects.filter(
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
            raise ValueError('Keine Behörde gefunden!')
        elif len(pbs) > 1:
            raise ValueError('Mehr als eine Behörde gefunden')
        return pbs[0]
