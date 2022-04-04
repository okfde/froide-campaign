from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from websockets.exceptions import ConnectionClosedOK

from froide.helper.presence import get_expiring_keys_manager

from .models import Campaign

PRESENCE_ROOM = "campaign.live.{}"


@sync_to_async
def get_campaign(campaign_id):
    try:
        return Campaign.objects.get(id=campaign_id)
    except Campaign.DoesNotExist:
        return None


RESERVATION_TIMEOUT = 5 * 60


def get_reservation_manager(campaign_id):
    return get_expiring_keys_manager(
        "campaign{}".format(campaign_id), timeout=RESERVATION_TIMEOUT
    )


class CampaignLiveConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.room = None
        self.campaign_id = self.scope["url_route"]["kwargs"]["pk"]

        campaign = await get_campaign(self.campaign_id)
        if not campaign:
            await self.close()
            return

        self.room = PRESENCE_ROOM.format(self.campaign_id)

        await self.channel_layer.group_add(self.room, self.channel_name)
        await self.accept()

        self.reservation_manager = None
        self.reservation_set = None
        if campaign.provider_kwargs.get("reservations"):
            self.reservation_set = set()
            self.reservation_manager = get_reservation_manager(self.campaign_id)
            await self.send_reservations()

    async def receive_json(self, content):
        if content["type"] == "heartbeat":
            return
        if self.reservation_manager:
            if content["type"] == "request_reservations":
                await self.send_reservations()
                return
            if content["type"] == "reserve":
                obj_id = content.get("obj_id")
                client_id = content.get("client_id")
                if not obj_id or not client_id:
                    return
                self.reservation_set.add((obj_id, client_id))
                await self.reservation_manager.add_key_value(obj_id, client_id)
                await self.trigger_reservations_resend()
                return
            if content["type"] == "unreserve":
                obj_id = content.get("obj_id")
                client_id = content.get("client_id")
                if not obj_id or not client_id:
                    return
                self.reservation_set.discard((obj_id, client_id))
                await self.reservation_manager.remove_key_value(obj_id, client_id)
                await self.trigger_reservations_resend()
                return
            if content["type"] == "reservations":
                await self.send_reservations()
                return

    async def send_reservations(self, reservations=None):
        if reservations is None:
            reservations = [x async for x in self.reservation_manager.list_key_value()]

        await self.send_json(
            {
                "type": "reservations",
                "reservations": reservations,
                "timeout": RESERVATION_TIMEOUT,
            }
        )

    async def trigger_reservations_resend(self):
        if not self.reservation_manager:
            return
        reservations = [x async for x in self.reservation_manager.list_key_value()]
        await self.channel_layer.group_send(
            self.room, {"type": "broadcast.reservations", "reservations": reservations}
        )

    async def broadcast_reservations(self, event):
        try:
            await self.send_reservations(reservations=event["reservations"])
        except ConnectionClosedOK:
            pass

    async def request_made(self, event):
        try:
            await self.send_json(
                {
                    "type": "request_made",
                    "data": event["data"],
                }
            )
            if self.reservation_manager:
                await self.reservation_manager.remove_key(event["data"]["id"])
                await self.trigger_reservations_resend()
        except ConnectionClosedOK:
            pass

    async def disconnect(self, close_code):
        if self.room is None:
            return

        if self.reservation_set:
            for obj_id, client_id in self.reservation_set:
                await self.reservation_manager.remove_key_value(obj_id, client_id)
            await self.trigger_reservations_resend()
        await self.channel_layer.group_discard(self.room, self.channel_name)
