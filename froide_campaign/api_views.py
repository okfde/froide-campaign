from django.conf import settings
from django.contrib.gis.geos import Point
from django.shortcuts import Http404, get_object_or_404

from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.throttling import UserRateThrottle

from froide.foirequest.api_views import throttle_action

from .geocode import run_geocode
from .models import (
    Answer,
    Campaign,
    CampaignSubscription,
    InformationObject,
    Question,
    Questionaire,
    Report,
)


def get_language(request):
    lang = request.GET.get("language", settings.LANGUAGE_CODE)
    if lang not in dict(settings.LANGUAGES):
        return settings.LANGUAGE_CODE
    return lang


class AddLocationPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        campaign_id = request.data.get("campaign")
        if campaign_id is None:
            return False
        campaign = Campaign.objects.get(id=campaign_id)
        return campaign.get_provider().CREATE_ALLOWED


class AddLocationThrottle(UserRateThrottle):
    scope = "campaign-createlocation"
    THROTTLE_RATES = {
        scope: "3/day",
    }


class InformationObjectViewSet(viewsets.GenericViewSet):
    RANDOM_COUNT = 3
    SEARCH_COUNT = 10
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS

    def get_provider(self):
        if not hasattr(self, "campaign"):
            self.campaign = self.get_campaign()
        self.provider = self.campaign.get_provider()
        return self.provider

    def get_campaign(self):
        campaign_id = self.request.GET.get("campaign")
        if self.request.user.is_staff:
            qs = Campaign.objects.all()
        else:
            qs = Campaign.objects.get_public()
        try:
            return get_object_or_404(qs, id=campaign_id)
        except ValueError:
            raise Http404

    def get_queryset(self):
        return self.provider.get_queryset()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update(
            {"language": get_language(self.request), "provider": self.provider}
        )
        return context

    def get_serializer(self, qs_obj, **kwargs):
        kwargs.setdefault("context", self.get_serializer_context())
        return self.provider.get_serializer(qs_obj, **kwargs)

    def get_permissions(self):
        if self.action == "create":
            permission_classes = [AddLocationPermission]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

    @throttle_action((AddLocationThrottle,))
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        obj = serializer.save()
        obj.ident = "custom_{}".format(str(obj.id))
        point = self.get_geo(obj)
        obj.geo = point
        obj.save()

    def retrieve(self, request, *args, **kwargs):
        campaign = self.get_campaign()
        language = get_language(self.request)
        campaign.set_current_language(language)
        provider = campaign.get_provider()
        ident = kwargs.pop("pk")
        serializer = provider.get_request_serializer(request, ident)
        return Response(serializer.data)

    def list(self, request):
        provider = self.get_provider()
        queryset = self.get_queryset()

        try:
            queryset = provider.search(self.request, queryset)
        except ValueError:
            return Response([])

        # TODO: move into non-base providers?
        # if not type(provider) == BaseProvider:
        #     try:
        #         iobjs = BaseProvider(self.campaign).search(**filters)
        #         data = data + iobjs
        #     except ValueError:
        #         return Response([])

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_geo(self, obj):
        if obj.address and not obj.geo:
            geo = run_geocode(obj.address)
            if geo:
                lat_lng = geo[0]
                return Point(lat_lng[1], lat_lng[0])

    @action(detail=False, methods=["post"])
    def report(self, request):
        questionaire_id = int(request.data.get("questionaire"))
        iobj_id = int(request.data.get("informationObject"))
        answers = request.data.get("answers")
        report_id = request.data.get("report")

        questionaire = Questionaire.objects.get(id=questionaire_id)
        information_object = InformationObject.objects.get(id=iobj_id)

        if report_id:
            report = Report.objects.get(id=report_id)
            report.answer_set.all().delete()
        else:
            report = Report.objects.create(
                questionaire=questionaire, informationsobject=information_object
            )

        for answer in answers:
            question_id = int(answer["questionId"])
            question = Question.objects.get(id=question_id)
            Answer.objects.create(
                text=answer["answer"], report=report, question=question
            )
        return Response({"report": report.id})

    @action(detail=False, methods=["post"])
    def subscribe(self, request):
        email = request.data.get("email")
        if request.user.is_authenticated:
            email = request.user.email

        campaign_id = request.data.get("campaign")
        subscribe = request.data.get("subscribe")

        if email and campaign_id:
            try:
                campaign = Campaign.objects.get(id=campaign_id)
                if subscribe:
                    obj, created = CampaignSubscription.objects.get_or_create(
                        campaign=campaign, email=email
                    )
                    return Response({"email": obj.email, "campaign": obj.campaign.id})
                else:
                    try:
                        obj = CampaignSubscription.objects.get(
                            campaign=campaign, email=email
                        ).delete()
                    except CampaignSubscription.DoesNotExist:
                        pass
            except Campaign.DoesNotExist:
                return Response({"error": "Campaign does not exist"})
        return Response({})
