from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from froide.publicbody.models import PublicBody

from .amenity import AmenityProvider


class AmenityLocalProvider(AmenityProvider):
    """
    Like Amenity provider but tries to find the public body
    for the amenity at its location
    """

    NEARBY_RADIUS = 200

    def _get_nearby_publicbodies(self, amenity):
        nearby_pbs = (
            PublicBody.objects.filter(geo__isnull=False)
            .filter(geo__dwithin=(amenity.geo, self.NEARBY_RADIUS))
            .filter(geo__distance_lte=(amenity.geo, D(m=self.NEARBY_RADIUS)))
        )
        return nearby_pbs

    def _get_same_name_pbs(self, amenity):
        return PublicBody.objects.filter(name=amenity.name)

    def _get_publicbody(self, amenity):
        same_name_pbs = self._get_same_name_pbs(amenity)
        if same_name_pbs and same_name_pbs.count() == 1:
            return same_name_pbs.first()

        nearby_pbs = (
            self._get_nearby_publicbodies(amenity)
            .annotate(distance=Distance("geo", amenity.geo))
            .order_by("-number_of_requests", "distance")
        )

        if nearby_pbs:
            by_name = nearby_pbs.filter(name=amenity.name)
            if by_name:
                return by_name.first()
            if self.kwargs.get("category"):
                by_cat = nearby_pbs.filter(categories__name=self.kwargs["category"])
                if by_cat:
                    return by_cat.first()
            return nearby_pbs.first()

        return super()._get_publicbody(amenity)

    def get_publicbodies(self, ident):
        amenity = self.get_by_ident(ident)
        same_name = self._get_same_name_pbs(amenity)
        nearby_pbs = self._get_nearby_publicbodies(amenity)
        with_cat = super().get_publicbodies(ident)
        return same_name.union(nearby_pbs, with_cat)
