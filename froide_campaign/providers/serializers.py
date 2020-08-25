from rest_framework import serializers


class CampaignProviderItemSerializer(serializers.Serializer):
    # TODO: remove foirequest
    title = serializers.CharField()
    request_url = serializers.CharField(required=False)
    publicbody_name = serializers.CharField(required=False)
    description = serializers.CharField()
    foirequest = serializers.IntegerField(min_value=0, required=False)
    foirequests = serializers.ListField(
        child=serializers.IntegerField(min_value=0), required=False
    )
    lat = serializers.FloatField(required=False)
    lng = serializers.FloatField(required=False)