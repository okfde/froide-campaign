from django.template.defaultfilters import slugify

from django_amenities.models import Amenity

from froide.publicbody.models import PublicBody
from froide.georegion.models import GeoRegion

from ..models import InformationObject

from .base import BaseProvider, first


class AmenityProvider(BaseProvider):
    CREATE_ALLOWED = True
    ADMIN_LEVELS = [
        'borough', 'municipality', 'admin_cooperation',
        'district', 'state'
    ]

    def get_queryset(self):
        iobs = super().get_queryset()
        ident_list = iobs.values_list('ident', flat=True)
        osm_ids = [int(ident.split('_')[1])
                   for ident in ident_list if 'custom' not in ident]
        return Amenity.objects.filter(
            topics__contains=[self.kwargs.get('amenity_topic', '')],
        ).exclude(name='').exclude(osm_id__in=osm_ids)

    def get_ident_list(self, qs):
        return [
            obj.ident for obj in qs
        ]

    def filter(self, qs, **filter_kwargs):
        if filter_kwargs.get('q'):
            qs = qs.filter(name__contains=filter_kwargs['q'])
        if filter_kwargs.get('requested') is not None:
            qs = qs.none()
        return qs

    def get_by_ident(self, ident):
        try:
            pk = ident.split('_')[0]
            return self.get_queryset().get(id=pk)
        except ValueError:
            return super().get_by_ident(ident)

    def get_provider_item_data(self, obj, foirequests=None, detail=False):
        d = {
            'ident': obj.ident,
            'request_url': self.get_request_url_redirect(obj.ident),
            'title': obj.name,
            'address': obj.address,
            'description': '',
            'lat': obj.geo.y,
            'lng': obj.geo.x,
            'foirequest': None,
            'foirequests': [],
        }

        if foirequests:
            d.update({
                'foirequest': first(foirequests[obj.ident]),
                'foirequests': foirequests[obj.ident]
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
        ).filter(
            kind__in=self.ADMIN_LEVELS
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

    def connect_request(self, ident, sender):
        if not sender.public:
            return

        try:
            amenity = self.get_by_ident(ident)
        except Amenity.DoesNotExist:
            return

        context = self.get_request_url_context(amenity)

        iobj, created = InformationObject.objects.get_or_create(
            campaign=self.campaign,
            ident=ident,
            defaults=dict(
                title=context['title'],
                slug=slugify(context['title']),
                publicbody=sender.public_body,
                geo=amenity.geo,
                foirequest=sender
            )
        )

        if not created:
            iobj.publicbody = sender.public_body
            iobj.save()

        iobj.foirequests.add(sender)
