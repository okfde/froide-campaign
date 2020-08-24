from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance

from django.shortcuts import Http404, get_object_or_404

from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Campaign, InformationObject


class InformationObjectSerializer(serializers.HyperlinkedModelSerializer):
    request_url = serializers.CharField(source='make_domain_request_url')
    publicbody_name = serializers.SerializerMethodField(
        source='get_publicbody_name'
    )
    description = serializers.CharField(source='get_description')
    foirequest = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:

        model = InformationObject
        fields = (
            'id', 'title', 'request_url',
            'description', 'publicbody_name',
            'foirequest'
        )

    def get_publicbody_name(self, obj):
        if obj.publicbody is None:
            return ''
        return obj.publicbody.name


class InformationObjectLocationSerializer(InformationObjectSerializer):
    lat = serializers.FloatField(source='get_latitude')
    lng = serializers.FloatField(source='get_longitude')
    foirequest = serializers.CharField(source='get_froirequest_url')
    foirequests = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='slug'
     )

    class Meta:

        model = InformationObject
        fields = (
            'id', 'title', 'request_url',
            'description', 'publicbody_name', 'foirequests',
            'foirequest', 'lat', 'lng'
        )


class InformationObjectViewSet(viewsets.ReadOnlyModelViewSet):
    RANDOM_COUNT = 3
    SEARCH_COUNT = 10
    serializer_class = InformationObjectSerializer

    def get_queryset(self):
        return InformationObject.objects.none()

    def get_lat_lng(self, request):
        try:
            lat = float(request.GET.get('lat'))
        except (ValueError, TypeError):
            raise ValueError
        try:
            lng = float(request.GET.get('lng'))
        except (ValueError, TypeError):
            raise ValueError
        return lat, lng

    @action(detail=False, methods=['get'])
    def map(self, request):
        campaign_ids = request.GET.getlist('campaign')
        try:
            campaign_ids = [int(x) for x in campaign_ids]
        except ValueError:
            raise Http404

        qs = InformationObject.objects.filter(
            publicbody__isnull=False,
            campaign_id__in=campaign_ids
        ).select_related('campaign', 'publicbody').order_by('?')

        query = request.GET.get('q')
        if query:
            qs = InformationObject.objects.search(qs, query)

        requested = request.GET.get('requested')
        if requested and requested == '1':
            qs = qs.filter(foirequests__isnull=False)

        '''
        radius = 10000
        try:
            radius = int(request.GET.get('radius'))
        except (ValueError, TypeError):
            pass

        point = None
        try:
            lat, lng = self.get_lat_lng(request)
            point = Point(lng, lat)
        except ValueError:
            pass

        if point and radius:
            qs = qs.filter(geo__distance_lt=(point, Distance(km=radius)))
        '''


        serializer = InformationObjectLocationSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def random(self, request):
        campaign_ids = request.GET.getlist('campaign')
        try:
            campaign_ids = [int(x) for x in campaign_ids]
        except ValueError:
            raise Http404

        qs = InformationObject.objects.filter(
            publicbody__isnull=False,
            campaign_id__in=campaign_ids, foirequests__isnull=True
        ).select_related('campaign', 'publicbody').order_by('?')
        qs = qs[:self.RANDOM_COUNT]
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

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
