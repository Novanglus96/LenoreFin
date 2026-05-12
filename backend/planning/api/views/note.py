from ninja import Router
from ninja.errors import HttpError
from planning.models import Note
from planning.api.schemas.note import NoteIn, NoteOut
from django.shortcuts import get_object_or_404
from django.http import Http404
from typing import List
import logging
from administration.api.dependencies.auth import FullAccessAuth

api_logger = logging.getLogger("api")
db_logger = logging.getLogger("db")
error_logger = logging.getLogger("error")
task_logger = logging.getLogger("task")

note_router = Router(tags=["Notes"])


@note_router.post("/create", auth=FullAccessAuth())
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
        api_logger.info(f"Note created : {note.note_date}")
        return {"id": note.id}
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Note not created")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record creation error")


@note_router.put("/update/{note_id}", auth=FullAccessAuth())
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
        api_logger.info(f"Note updated : #{note_id}")
        return {"success": True}
    except Http404:
        raise HttpError(404, "Note not found")
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Note not updated")
        error_logger.error(f"{str(e)}")
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
        api_logger.debug(f"Note retrieved : #{note.id}")
        return note
    except Http404:
        raise HttpError(404, "Note not found")
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Note not retrieved")
        error_logger.error(f"{str(e)}")
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
        api_logger.debug("Note list retrieved")
        return qs
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Note list not retrieved")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record retrieval error")


@note_router.delete("/delete/{note_id}", auth=FullAccessAuth())
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
        api_logger.info(f"Note deleted from {note_date}")
        return {"success": True}
    except Http404:
        raise HttpError(404, "Note not found")
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Note not deleted")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record retrieval error")
