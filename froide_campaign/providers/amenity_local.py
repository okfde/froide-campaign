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

        same_name_pbs = PublicBody.objects.filter(name=amenity.name)
        if same_name_pbs and same_name_pbs.count() == 1:
            return same_name_pbs.first()

        nearby_pbs = PublicBody.objects.filter(
            geo__isnull=False
        ).filter(
            geo__dwithin=(amenity.geo, self.NEARBY_RADIUS)
        ).filter(
            geo__distance_lte=(amenity.geo, D(m=self.NEARBY_RADIUS))
        ).annotate(
            distance=Distance("geo", amenity.geo)
        ).order_by("-number_of_requests", "distance")

        if nearby_pbs:
            by_name = nearby_pbs.filter(name=amenity.name)
            if by_name:
                return by_name.first()
            if self.kwargs.get('category'):
                by_cat = nearby_pbs.filter(
                    categories__name=self.kwargs['category']
                )
                if by_cat:
                    return by_cat.first()
            return nearby_pbs.first()

        return super()._get_publicbody(amenity)
