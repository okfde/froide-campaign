import random

from django.contrib.gis.geos import Point
from django.shortcuts import get_object_or_404

from rest_framework import filters
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.throttling import UserRateThrottle
from rest_framework.decorators import action

from froide.foirequest.api_views import throttle_action

from .models import (Campaign, InformationObject,
                     CampaignSubscription, Questionaire,
                     Question, Report, Answer)

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


class StatusFilter(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        if request.GET.get('status'):
            status = request.GET.get('status')
            if status == 'normal':
                return queryset.filter(foirequests__isnull=True)
            if status == 'pending':
                return queryset.filter(foirequests__isnull=False).exclude(
                    foirequests__status='resolved')
            if status == 'successful':
                successful = ['successful', 'partially_successful']
                return queryset.filter(foirequests__status='resolved',
                                       foirequests__resolution__in=successful)
            if status == 'refused':
                return queryset.filter(foirequests__status='resolved',
                                       foirequests__resolution='refused')
        return queryset


class TagFilter(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        if request.GET.get('tag'):
            tag = request.GET.get('tag')
            return queryset.filter(tags__contains=tag)
        return queryset


class InformationObjectViewSet(mixins.CreateModelMixin,
                               mixins.RetrieveModelMixin,
                               mixins.ListModelMixin,
                               viewsets.GenericViewSet):
    RANDOM_COUNT = 3
    SEARCH_COUNT = 10
    serializer_class = InformationObjectSerializer
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    filter_backends = [filters.SearchFilter, StatusFilter, TagFilter]
    search_fields = ['title', 'subtitle', 'address', 'ident']

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
        data['publicbodies'] = provider.get_publicbodies(ident)
        data['makeRequestURL'] = provider.get_request_url(ident)

        serializer = CampaignProviderRequestSerializer(
            data, context={'request': request}
        )
        return Response(serializer.data)

    def get_queryset(self):
        campaign_id = self.request.GET.get('campaign')
        campaign = get_object_or_404(
            Campaign.objects.get_public(),
            id=campaign_id
        )
        if campaign:
            return InformationObject.objects.filter(campaign=campaign)
        return InformationObject.objects.none()

    def get_geo(self, obj):
        if obj.address and not obj.geo:
            geo = run_geocode(obj.address)
            if geo:
                lat_lng = geo[0]
                return Point(lat_lng[1], lat_lng[0])

    @action(detail=False, methods=['post'])
    def report(self, request):
        questionaire_id = int(request.data.get('questionaire'))
        iobj_id = int(request.data.get('informationObject'))
        answers = request.data.get('answers')
        report_id = request.data.get('report')

        questionaire = Questionaire.objects.get(id=questionaire_id)
        information_object = InformationObject.objects.get(id=iobj_id)

        if report_id:
            report = Report.objects.get(id=report_id)
            report.answer_set.all().delete()
        else:
            report = Report.objects.create(
                questionaire=questionaire,
                informationsobject=information_object
            )

        for answer in answers:
            question_id = int(answer['questionId'])
            question = Question.objects.get(id=question_id)
            Answer.objects.create(
                text=answer['answer'],
                report=report,
                question=question
            )
        return Response({
            'report': report.id
        })

    @action(detail=False, methods=['post'])
    def subscribe(self, request):
        email = request.data.get('email')
        if request.user.is_authenticated:
            email = request.user.email

        campaign_id = request.data.get('campaign')
        subscribe = request.data.get('subscribe')

        if email and campaign_id:
            try:
                campaign = Campaign.objects.get(id=campaign_id)
                if subscribe:
                    obj, created = CampaignSubscription.objects.get_or_create(
                        campaign=campaign, email=email)
                    return Response({
                        'email': obj.email,
                        'campaign': obj.campaign.id
                    })
                else:
                    try:
                        obj = CampaignSubscription.objects.get(
                            campaign=campaign, email=email).delete()
                    except CampaignSubscription.DoesNotExist:
                        pass
            except Campaign.DoesNotExist:
                return Response({
                    'error': 'Campaign does not exist'
                })
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
            'q': request.GET.get('q', '')
        }

        try:
            if'featured' in request.GET:
                filters['featured'] = int(request.GET['featured'])
        except ValueError:
            pass

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

        if not type(provider) == BaseProvider:
            iobjs = BaseProvider(campaign).search(**filters)
            data = data + iobjs

        return Response(data)
