from django.urls import path
from core.consumers import SyncConsumer

websocket_urlpatterns = [
    path("ws/sync/", SyncConsumer.as_asgi()),
]
