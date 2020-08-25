import random

from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Campaign, InformationObject

from .providers.serializers import CampaignProviderItemSerializer


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
            'requested': bool(request.GET.get('requested'))
        }

        # TODO: geocode
        # location / coordinates
        # if location is not None:
        #     location_search = True
        #     point, formatted_address = geocode(location, address=False)
        # elif coordinates is not None:
        #     point = Point(coordinates[1], coordinates[0])


        data = provider.search(**filters)
        return Response(data)
