from froide.publicbody.api_views import PublicBodySerializer
from rest_framework import serializers

from .models import InformationObject


class CampaignProviderItemSerializer(serializers.Serializer):
    ident = serializers.CharField()
    title = serializers.CharField()
    address = serializers.CharField(required=False)
    request_url = serializers.CharField(required=False)
    publicbody_name = serializers.CharField(required=False)
    description = serializers.CharField()
    # TODO: remove foirequest
    foirequest = serializers.IntegerField(min_value=0, required=False)
    foirequests = serializers.ListField(
        child=serializers.IntegerField(min_value=0), required=False
    )
    lat = serializers.FloatField(required=False)
    lng = serializers.FloatField(required=False)


class CampaignProviderRequestSerializer(serializers.Serializer):
    ident = serializers.CharField()
    lat = serializers.FloatField(required=False)
    lng = serializers.FloatField(required=False)
    name = serializers.CharField(required=False)
    address = serializers.CharField(required=False)
    publicbody = PublicBodySerializer(required=False)
    publicbodies = PublicBodySerializer(many=True, required=False)
    makeRequestURL = serializers.CharField(required=False)


class InformationObjectSerializer(serializers.ModelSerializer):
    lat = serializers.FloatField(source='get_latitude', required=False)
    lng = serializers.FloatField(source='get_longitude', required=False)
    ident = serializers.CharField(required=False)
    request_url = serializers.SerializerMethodField()

    class Meta:
        model = InformationObject
        fields = (
            'title', 'address', 'campaign', 'lat', 'lng',
            'request_url', 'foirequests', 'ident'
        )

    def get_request_url(self, obj):
        provider = obj.campaign.get_provider()
        return provider.get_request_url_redirect(obj.ident)
