import json
from channels.generic.websocket import AsyncWebsocketConsumer


class SyncConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if not user.is_authenticated:
            await self.close()
            return
        await self.channel_layer.group_add("global", self.channel_name)
        await self.channel_layer.group_add(f"user_{user.pk}", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        user = self.scope.get("user")
        await self.channel_layer.group_discard("global", self.channel_name)
        if user and user.is_authenticated:
            await self.channel_layer.group_discard(f"user_{user.pk}", self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        pass

    async def sync_invalidate(self, event):
        await self.send(text_data=json.dumps({
            "type": "invalidate",
            "keys": event["keys"],
        }))
