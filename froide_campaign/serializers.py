from froide.publicbody.api_views import PublicBodySerializer
from rest_framework import serializers

from .models import InformationObject


class CampaignProviderItemSerializer(serializers.Serializer):
    ident = serializers.CharField()
    title = serializers.CharField()
    subtitle = serializers.CharField(required=False)
    address = serializers.CharField(required=False)
    request_url = serializers.CharField(required=False)
    publicbody_name = serializers.CharField(required=False)
    description = serializers.CharField()
    foirequest = serializers.IntegerField(min_value=0, required=False)
    foirequests = serializers.ListField(child=serializers.DictField(required=False))
    lat = serializers.FloatField(required=False)
    lng = serializers.FloatField(required=False)
    resolution = serializers.CharField(required=False)
    public = serializers.BooleanField(default=True)
    context = serializers.DictField(required=False)
    categories = serializers.ListField(required=False)
    featured = serializers.BooleanField(required=False)


class CampaignProviderRequestSerializer(serializers.Serializer):
    ident = serializers.CharField()
    lat = serializers.FloatField(required=False)
    lng = serializers.FloatField(required=False)
    name = serializers.CharField(required=False)
    address = serializers.CharField(required=False)
    publicbody = PublicBodySerializer(required=False)
    publicbodies = PublicBodySerializer(many=True, required=False)
    makeRequestURL = serializers.CharField(required=False)
    userRequestCount = serializers.IntegerField(required=False)
    public = serializers.BooleanField(default=True)


class InformationObjectSerializer(serializers.ModelSerializer):
    lat = serializers.FloatField(source="get_latitude", required=False)
    lng = serializers.FloatField(source="get_longitude", required=False)
    ident = serializers.CharField(required=False)
    request_url = serializers.SerializerMethodField()
    resolution = serializers.SerializerMethodField()
    foirequest = serializers.SerializerMethodField()
    public = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    subtitle = serializers.SerializerMethodField()

    class Meta:
        model = InformationObject
        fields = (
            "title",
            "subtitle",
            "address",
            "campaign",
            "lat",
            "lng",
            "request_url",
            "foirequests",
            "ident",
            "resolution",
            "id",
            "foirequest",
            "public",
            "categories",
        )

    def get_title(self, obj):
        obj.set_current_language(self.context.get("language"))
        return obj.title

    def get_subtitle(self, obj):
        obj.set_current_language(self.context.get("language"))
        return obj.subtitle

    def get_categories(self, obj):
        categories = obj.categories.language(self.context.get("language"))
        return [{"id": cat.id, "title": cat.title} for cat in categories]

    def get_request_url(self, obj):
        provider = obj.campaign.get_provider()
        return provider.get_request_url_redirect(obj.ident)

    def get_foirequest(self, obj):
        foirequest = obj.get_best_foirequest()
        if foirequest:
            return foirequest.id

    def get_public(self, obj):
        return obj.get_public()

    def get_resolution(self, obj):
        return obj.get_resolution()

    def create(self, validated_data):
        title = self.context.get("request").data.get("title")
        iobj = InformationObject.objects.create(**validated_data)
        iobj.title = title
        iobj.save()
        return iobj
