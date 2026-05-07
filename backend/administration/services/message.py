from administration.models import Message
from administration.api.schemas.message import MessageList, MessageOut


def get_message_list() -> MessageList:
    """
    Build a MessageList containing unread count, total count, and all messages
    ordered by id descending.

    Returns:
        MessageList: a message list object with unread_count, total_count, and messages.
    """
    unread = Message.objects.filter(unread=True).count()
    total = Message.objects.all().count()
    messages = Message.objects.all().order_by("-id")
    message_list = [MessageOut.from_orm(message) for message in messages]
    return MessageList(
        unread_count=unread, total_count=total, messages=message_list
    )
