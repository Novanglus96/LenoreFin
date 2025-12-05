from ninja import Router
from ninja.errors import HttpError
from administration.models import Message
from administration.api.schemas.message import (
    MessageIn,
    MessageList,
    MessageOut,
    AllMessage,
)
from django.shortcuts import get_object_or_404
import logging

api_logger = logging.getLogger("api")
db_logger = logging.getLogger("db")
error_logger = logging.getLogger("error")
task_logger = logging.getLogger("task")

message_router = Router(tags=["Messages"])


@message_router.post("/create")
def create_message(request, payload: MessageIn):
    """
    The function `create_transaction_detail` creates a transaction detail

    Args:
        request ():
        payload (TransactionDetailIn): An object using schema of TransactionDetailIn.

    Returns:
        id: returns the id of the created transaction detail
    """

    try:
        message = Message.objects.create(**payload.dict())
        api_logger.info(f"Message created : #{message.id}")
        return {"id": message.id}
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Message not created")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record creation error")


@message_router.put("/update/{message_id}")
def update_message(request, message_id: int, payload: MessageIn):
    """
    The function `update_message` updates the message specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        message_id (int): the id of the message to update
        payload (MessageIn): a message object

    Returns:
        success: True

    Raises:
        Http404: If the message with the specified ID does not exist.
    """

    try:
        message = get_object_or_404(Message, id=message_id)
        message.message_date = payload.message_date
        message.message = payload.message
        message.unread = payload.unread
        message.save()
        api_logger.info(f"Message updated : {message_id}")
        return {"sucess": True}
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Message not updated")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record update error")


@message_router.patch("/readall/{message_id}")
def update_messages(request, message_id: int, payload: AllMessage):
    """
    The function `update_messages` marks all messages as read.

    Args:
        request (HttpRequest): The HTTP request object.
        message_id (int): defaults to 0 and is unused
        payload (AllMessage): an all message object

    Returns:
        success: True
    """
    try:
        messages = Message.objects.all()

        for message in messages:
            message.unread = payload.unread
            message.save()
        api_logger.info("All messages marked as read")
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Messages not marked as read")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Messages not marked read error")


@message_router.get("/get/{message_id}", response=MessageOut)
def get_message(request, message_id: int):
    """
    The function `get_message` retrieves the message by id

    Args:
        request (HttpRequest): The HTTP request object.
        message_id (int): The id of the message to retrieve.

    Returns:
        MessageOut: the message object

    Raises:
        Http404: If the message with the specified ID does not exist.
    """

    try:
        message = get_object_or_404(Message, id=message_id)
        api_logger.debug(f"Message retrieved : {message.id}")
        return message
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Message not retrieved")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record retrieval error")


@message_router.delete("/delete/{message_id}")
def delete_message(request, message_id: int):
    """
    The function `delete_message` deletes the message specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        message_id (int): the id of the message to delete

    Returns:
        success: True

    Raises:
        Http404: If the message with the specified ID does not exist.
    """

    try:
        message = get_object_or_404(Message, id=message_id)
        message.delete()
        api_logger.info(f"Message deleted : #{message_id}")
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Message not deleted")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record retrieval error")


@message_router.delete("/deleteall/{message_id}")
def delete_messages(request, message_id: int):
    """
    The function `delete_messages` deletes all messages.

    Args:
        request (HttpRequest): The HTTP request object.
        message_id (int): defaults to 0, not used

    Returns:
        success: True
    """

    try:
        messages = Message.objects.all()
        for message in messages:
            message.delete()
        api_logger.info("All Messages deleted")
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("All messages not deleted")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record retrieval error")


@message_router.get("/list", response=MessageList)
def list_messages(request):
    """
    The function `list_messages` retrieves a list of messages,
    ordered by id descending.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        MessageList: a message list object that includes unread and totals.
    """

    try:
        unread = Message.objects.filter(
            unread=True
        ).count()  # Total unread messages
        total = Message.objects.all().count()  # The total number of messages
        messages = Message.objects.all().order_by("-id")
        message_list = []
        for message in messages:
            message_list.append(MessageOut.from_orm(message))
        message_list_object = MessageList(
            unread_count=unread, total_count=total, messages=message_list
        )
        api_logger.debug("Message list retrieved")
        return message_list_object
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Message list not retrieved")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record retrieval error")
