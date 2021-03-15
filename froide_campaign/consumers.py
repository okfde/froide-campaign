from asgiref.sync import sync_to_async
from websockets.exceptions import ConnectionClosedOK
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from .models import Campaign

PRESENCE_ROOM = 'campaign.live.{}'


@sync_to_async
def get_campaign(campaign_id):
    try:
        return Campaign.objects.get(id=campaign_id)
    except Campaign.DoesNotExist:
        return None


class CampaignLiveConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.room = None
        self.campaign_id = self.scope['url_route']['kwargs']['pk']

        campaign = await get_campaign(self.campaign_id)
        if not campaign:
            await self.close()
            return

        self.room = PRESENCE_ROOM.format(self.campaign_id)

        await self.channel_layer.group_add(
            self.room,
            self.channel_name
        )
        await self.accept()

    async def receive_json(self, content):
        if content['type'] == 'heartbeat':
            return

    async def request_made(self, event):
        try:
            await self.send_json({
                'type': 'request_made',
                'data': event['data'],
            })
        except ConnectionClosedOK:
            pass

    async def disconnect(self, close_code):
        if self.room is None:
            return

        await self.channel_layer.group_discard(
            self.room,
            self.channel_name
        )
