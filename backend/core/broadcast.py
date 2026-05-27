from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import logging

error_logger = logging.getLogger("error")


def broadcast_invalidate(keys: list, group: str = "global"):
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return
    try:
        async_to_sync(channel_layer.group_send)(
            group,
            {"type": "sync.invalidate", "keys": keys},
        )
    except Exception as e:
        error_logger.warning(f"WebSocket broadcast failed: {e}")
