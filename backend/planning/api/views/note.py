from ninja import Router, Query
from django.db import IntegrityError
from ninja.errors import HttpError
from planning.models import Note
from planning.api.schemas.note import NoteIn, NoteOut
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

note_router = Router(tags=["Notes"])


@note_router.post("/create")
def create_note(request, payload: NoteIn):
    """
    The function `create_note` creates a note

    Args:
        request ():
        payload (NoteIn): An object using schema of NoteIn.

    Returns:
        id: returns the id of the created note
    """

    try:
        note = Note.objects.create(**payload.dict())
        logToDB(
            f"Note created : {note.note_date}",
            None,
            None,
            None,
            3001005,
            2,
        )
        return {"id": note.id}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Note not created : {str(e)}",
            None,
            None,
            None,
            3001901,
            2,
        )
        raise HttpError(500, "Record creation error")


@note_router.put("/update/{note_id}")
def update_note(request, note_id: int, payload: NoteIn):
    """
    The function `update_note` updates the note specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        note_id (int): the id of the note to update
        payload (NoteIn): a note object

    Returns:
        success: True

    Raises:
        Http404: If the note with the specified ID does not exist.
    """

    try:
        note = get_object_or_404(Note, id=note_id)
        note.note_text = payload.note_text
        note.note_date = payload.note_date
        note.save()
        logToDB(
            f"Note updated : #{note_id}",
            None,
            None,
            None,
            3001002,
            1,
        )
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Note not updated : {str(e)}",
            None,
            None,
            None,
            3001902,
            2,
        )
        raise HttpError(500, "Record update error")


@note_router.get("/get/{note_id}", response=NoteOut)
def get_note(request, note_id: int):
    """
    The function `get_note` retrieves the note by id

    Args:
        request (HttpRequest): The HTTP request object.
        note_id (int): The id of the note to retrieve.

    Returns:
        NoteOut: the note object

    Raises:
        Http404: If the note with the specified ID does not exist.
    """

    try:
        note = get_object_or_404(Note, id=note_id)
        logToDB(
            f"Note retrieved : #{note.id}",
            None,
            None,
            None,
            3001006,
            1,
        )
        return note
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Note not retrieved : {str(e)}",
            None,
            None,
            None,
            3001904,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@note_router.get("/list", response=List[NoteOut])
def list_notes(request):
    """
    The function `list_notes` retrieves a list of notes,
    ordered by note date descending.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        NoteOut: a list of note objects
    """

    try:
        qs = Note.objects.all().order_by("-note_date", "-id")
        logToDB(
            "Note list retrieved",
            None,
            None,
            None,
            3001007,
            1,
        )
        return qs
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Note list not retrieved : {str(e)}",
            None,
            None,
            None,
            3001907,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@note_router.delete("/delete/{note_id}")
def delete_note(request, note_id: int):
    """
    The function `delete_note` deletes the note specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        note_id (int): the id of the note to delete

    Returns:
        success: True

    Raises:
        Http404: If the note with the specified ID does not exist.
    """

    try:
        note = get_object_or_404(Note, id=note_id)
        note_date = note.note_date
        note.delete()
        logToDB(
            f"Note deleted from {note_date}",
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
            f"Note not deleted : {str(e)}",
            None,
            None,
            None,
            3001903,
            2,
        )
        raise HttpError(500, "Record retrieval error")
