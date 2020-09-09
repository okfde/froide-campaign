import random

from django.contrib.gis.geos import Point
from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Campaign, InformationObject

from .serializers import InformationObjectSerializer
from .geocode import run_geocode

from .providers.base import BaseProvider


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

class AddLocationPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        campaign_id = request.data.get('campaign')
        campaign = Campaign.objects.get(id=campaign_id)
        return campaign.get_provider().CREATE_ALLOWED


class InformationObjectViewSet(viewsets.ModelViewSet):
    RANDOM_COUNT = 3
    SEARCH_COUNT = 10
    serializer_class = InformationObjectSerializer

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [AddLocationPermission]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        obj = serializer.save()
        obj.ident = 'custom_{}'.format(str(obj.id))
        point = self.get_geo(obj)
        obj.geo = point
        obj.save()

    def get_queryset(self):
        return InformationObject.objects.none()

    def get_geo(self, obj):
        if obj.address and not obj.geo:
            geo = run_geocode(obj.address)
            if geo:
                lat_lng = geo[0]
                return Point(lat_lng[1], lat_lng[0])

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
        iobjs = BaseProvider(campaign).search(**filters)
        data = data + iobjs
        return Response(data)
