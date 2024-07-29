from ninja import Router, Query
from django.db import IntegrityError
from ninja.errors import HttpError
from administration.models import Message
from administration.api.schemas.message import (
    MessageIn,
    MessageList,
    MessageOut,
    AllMessage,
)
from administration.api.dependencies.log_to_db import logToDB
from django.shortcuts import get_object_or_404
from typing import List
from django.db.models import (
    Case,
    When,
    Q,
    IntegerField,
    Value,
    F,
    CharField,
    Sum,
    Subquery,
    OuterRef,
    FloatField,
    Window,
    ExpressionWrapper,
    DecimalField,
    Func,
    Count,
)
from django.db.models.functions import Concat, Coalesce, Abs
from typing import List, Optional, Dict, Any

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
        logToDB(
            f"Message created : #{message.id}",
            None,
            None,
            None,
            3001001,
            1,
        )
        return {"id": message.id}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Message not created : {str(e)}",
            None,
            None,
            None,
            3001901,
            2,
        )
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
        logToDB(
            f"Message updated : {message_id}",
            None,
            None,
            None,
            3001002,
            1,
        )
        return {"sucess": True}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Message not updated : {str(e)}",
            None,
            None,
            None,
            3001902,
            2,
        )
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
        logToDB(
            "All messages marked as read",
            None,
            None,
            None,
            3002006,
            1,
        )
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Messages not marked as read : {str(e)}",
            None,
            None,
            None,
            3002906,
            2,
        )
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
        logToDB(
            f"Message retrieved : {message.id}",
            None,
            None,
            None,
            3001006,
            1,
        )
        return message
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Message not retrieved : {str(e)}",
            None,
            None,
            None,
            3001904,
            2,
        )
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
        logToDB(
            f"Message deleted : #{message_id}",
            None,
            None,
            None,
            3001003,
            1,
        )
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Message not deleted : {str(e)}",
            None,
            None,
            None,
            3001903,
            2,
        )
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
        logToDB(
            "All Messages deleted",
            None,
            None,
            None,
            3001003,
            1,
        )
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"All messages not deleted : {str(e)}",
            None,
            None,
            None,
            3001903,
            2,
        )
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
        logToDB(
            "Message list retrieved",
            None,
            None,
            None,
            3001007,
            1,
        )
        return message_list_object
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Message list not retrieved : {str(e)}",
            None,
            None,
            None,
            3001907,
            2,
        )
        raise HttpError(500, "Record retrieval error")
