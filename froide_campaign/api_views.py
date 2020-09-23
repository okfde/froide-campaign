import random

from django.contrib.gis.geos import Point
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.decorators import action

from froide.foirequest.api_views import throttle_action

from .models import Campaign, InformationObject, CampaignSubscription

from .serializers import InformationObjectSerializer
from .serializers import CampaignProviderRequestSerializer
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
        if campaign_id is None:
            return False
        campaign = Campaign.objects.get(id=campaign_id)
        return campaign.get_provider().CREATE_ALLOWED


class AddLocationThrottle(UserRateThrottle):
    scope = 'campaign-createlocation'
    THROTTLE_RATES = {
        scope: '3/day',
    }


class InformationObjectViewSet(mixins.CreateModelMixin,
                               mixins.RetrieveModelMixin,
                               viewsets.GenericViewSet):
    RANDOM_COUNT = 3
    SEARCH_COUNT = 10
    serializer_class = InformationObjectSerializer

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [AddLocationPermission]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

    @throttle_action((AddLocationThrottle,))
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        obj = serializer.save()
        obj.ident = 'custom_{}'.format(str(obj.id))
        point = self.get_geo(obj)
        obj.geo = point
        obj.save()

    def retrieve(self, request, *args, **kwargs):
        campaign_id = request.GET.get('campaign')
        campaign = get_object_or_404(
            Campaign.objects.get_public(),
            id=campaign_id
        )
        provider = campaign.get_provider()
        ident = kwargs.pop('pk')
        obj = provider.get_by_ident(ident)
        data = provider.get_provider_item_data(obj)
        data['publicbody'] = provider.get_publicbody(ident)
        data['makeRequestURL'] = provider.get_request_url(ident)

        serializer = CampaignProviderRequestSerializer(
            data, context={'request': request}
        )
        return Response(serializer.data)

    def get_queryset(self):
        return InformationObject.objects.none()

    def get_geo(self, obj):
        if obj.address and not obj.geo:
            geo = run_geocode(obj.address)
            if geo:
                lat_lng = geo[0]
                return Point(lat_lng[1], lat_lng[0])

    @action(detail=False, methods=['post'])
    def subscribe(self, request):
        email = request.data.get('email')
        campaign_id = request.data.get('campaign')
        if email and campaign_id:
            campaign = Campaign.objects.get(id=campaign_id)
            obj, created = CampaignSubscription.objects.get_or_create(
                campaign=campaign, email=email)
            resp_data = {
                'email': obj.email,
                'campaign': obj.campaign.id
            }
            return Response(resp_data)
        return Response({})

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
