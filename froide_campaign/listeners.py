from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .consumers import PRESENCE_ROOM
from .models import Campaign


def connect_info_object(sender, **kwargs):
    reference = kwargs.get('reference')
    if not reference:
        reference = sender.reference
    if not reference:
        return
    if not reference.startswith('campaign:'):
        return
    namespace, campaign_value = reference.split(':', 1)
    try:
        campaign, ident = campaign_value.split('@', 1)
    except (ValueError, IndexError):
        return

    if not ident:
        return

    try:
        campaign_pk = int(campaign)
    except ValueError:
        return

    try:
        campaign = Campaign.objects.get(pk=campaign_pk)
    except Campaign.DoesNotExist:
        return

    provider = campaign.get_provider()
    iobj = provider.connect_request(ident, sender)
    if iobj:
        broadcast_request_made(provider, iobj)


def broadcast_request_made(provider, iobj):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        PRESENCE_ROOM.format(provider.campaign.id), {
            "type": "request_made",
            "data": provider.get_detail_data(iobj)
        }
    )
