from django.db.models import Q
from administration.models import Message
from administration.api.schemas.message import MessageList, MessageOut


def get_message_list(user=None) -> MessageList:
    """
    Build a MessageList for the given user: global messages (user=null) plus
    messages owned by this user. If no user provided, returns only global messages.
    """
    qs = Message.objects.filter(Q(user__isnull=True) | Q(user=user)) if user else Message.objects.filter(user__isnull=True)
    unread = qs.filter(unread=True).count()
    total = qs.count()
    messages = qs.order_by("-id")
    message_list = [MessageOut.from_orm(message) for message in messages]
    return MessageList(
        unread_count=unread, total_count=total, messages=message_list
    )
