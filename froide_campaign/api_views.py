import random

from django.shortcuts import get_object_or_404
from django.contrib.gis.geos import Point

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Campaign, InformationObject

from .providers.serializers import CampaignProviderItemSerializer


def get_lat_lng(request):
    try:
        lat = float(request.GET.get('lat'))
    except (ValueError, TypeError):
        raise ValueError
    try:
        lng = float(request.GET.get('lng'))
    except (ValueError, TypeError):
        raise ValueError
    return lat, lng


class InformationObjectViewSet(viewsets.ReadOnlyModelViewSet):
    RANDOM_COUNT = 3
    SEARCH_COUNT = 10
    serializer_class = CampaignProviderItemSerializer

    def get_queryset(self):
        return InformationObject.objects.none()

    @action(detail=False, methods=['get'])
    def random(self, request):
        campaign_id = request.GET.get('campaign')
        campaign = get_object_or_404(
            Campaign.objects.get_public(),
            id=campaign_id
        )

        provider = campaign.get_provider()

        filters = {
            'requested': False
        }

        data = provider.search(**filters)
        random_data = random.choices(data, k=self.RANDOM_COUNT)
        return Response(random_data)

    @action(detail=False, methods=['get'])
    def search(self, request):
        campaign_id = request.GET.get('campaign')
        campaign = get_object_or_404(
            Campaign.objects.get_public(),
            id=campaign_id
        )

        provider = campaign.get_provider()
        filters = {
            'q': request.GET.get('q', ''),
        }

        try:
            if'requested' in request.GET:
                filters['requested'] = int(request.GET['requested'])
        except ValueError:
            pass

        # TODO: geocode
        # location / coordinates
        # if location is not None:
        #     location_search = True
        #     point, formatted_address = geocode(location, address=False)

        try:
            lat, lng = get_lat_lng(request)
            filters.update({
                'coordinates': Point(lng, lat),
            })
        except ValueError:
            pass

        try:
            filters['zoom'] = int(request.GET.get('zoom'))
        except (ValueError, TypeError):
            pass
        try:
            filters['radius'] = int(request.GET.get('radius'))
        except (ValueError, TypeError):
            pass

        data = provider.search(**filters)
        return Response(data)
