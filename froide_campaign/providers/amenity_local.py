from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance

from froide.publicbody.models import PublicBody


from .amenity import AmenityProvider


class AmenityLocalProvider(AmenityProvider):
    '''
    Like Amenity provider but tries to find the public body
    for the amenity at its location
    '''
    NEARBY_RADIUS = 200

    def _get_publicbody(self, amenity):
        nearby_pbs = PublicBody.objects.filter(
            geo__isnull=False
        ).filter(
            geo__dwithin=(amenity.geo, self.NEARBY_RADIUS)
        ).filter(
            geo__distance_lte=(amenity.geo, D(m=self.NEARBY_RADIUS))
        ).annotate(
            distance=Distance("geo", amenity.geo)
        ).order_by("distance")[:1]

        if nearby_pbs:
            return nearby_pbs[0]

        return super()._get_publicbody(amenity)
