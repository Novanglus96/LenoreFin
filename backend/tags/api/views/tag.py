from ninja import Router, Query
from django.db import IntegrityError
from ninja.errors import HttpError
from tags.models import Tag, SubTag, MainTag
from tags.api.schemas.tag import TagIn, TagOut
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

tag_router = Router(tags=["Tags"])


@tag_router.post("/create")
def create_tag(request, payload: TagIn):
    """
    The function `create_tag` creates a tag

    Args:
        request ():
        payload (TagIn): An object using schema of TagIn.

    Returns:
        id: returns the id of the created tag
    """

    try:
        if payload.parent_name:
            try:
                parent = MainTag.objects.create(
                    tag_name=payload.parent_name,
                    tag_type_id=payload.tag_type_id,
                )
                payload.parent_id = parent.id
            except IntegrityError as integrity_error:
                # Check if the integrity error is due to a duplicate
                if "unique constraint" in str(integrity_error).lower():
                    logToDB(
                        f"Tag not created : tag exists",
                        None,
                        None,
                        None,
                        3001004,
                        2,
                    )
                    raise HttpError(400, "Tag already exists")
                else:
                    # Log other types of integry errors
                    logToDB(
                        "Tag not created : db integrity error",
                        None,
                        None,
                        None,
                        3001005,
                        2,
                    )
                    raise HttpError(400, "DB integrity error")
            except Exception as e:
                # Log other types of exceptions
                logToDB(
                    f"Tag not created : {str(e)}",
                    None,
                    None,
                    None,
                    3001901,
                    2,
                )
                raise HttpError(500, "Record creation error")
        if payload.child_name:
            try:
                child = SubTag.objects.create(
                    tag_name=payload.child_name,
                    tag_type_id=payload.tag_type_id,
                )
                payload.child_id = child.id
            except IntegrityError as integrity_error:
                # Check if the integrity error is due to a duplicate
                if "unique constraint" in str(integrity_error).lower():
                    logToDB(
                        f"Tag not created : tag exists",
                        None,
                        None,
                        None,
                        3001004,
                        2,
                    )
                    raise HttpError(400, "Tag already exists")
                else:
                    # Log other types of integry errors
                    logToDB(
                        "Tag not created : db integrity error",
                        None,
                        None,
                        None,
                        3001005,
                        2,
                    )
                    raise HttpError(400, "DB integrity error")
            except Exception as e:
                # Log other types of exceptions
                logToDB(
                    f"Tag not created : {str(e)}",
                    None,
                    None,
                    None,
                    3001901,
                    2,
                )
                raise HttpError(500, "Record creation error")
        tag = Tag.objects.create(
            parent_id=payload.parent_id,
            child_id=payload.child_id,
            tag_type_id=payload.tag_type_id,
        )
        logToDB(
            f"Tag created : {tag.tag_name}",
            None,
            None,
            None,
            3001001,
            1,
        )
        return {"id": tag.id}
    except IntegrityError as integrity_error:
        # Check if the integrity error is due to a duplicate
        if "unique constraint" in str(integrity_error).lower():
            logToDB(
                f"Tag not created : tag exists",
                None,
                None,
                None,
                3001004,
                2,
            )
            raise HttpError(400, "Tag already exists")
        else:
            # Log other types of integry errors
            logToDB(
                "Tag not created : db integrity error",
                None,
                None,
                None,
                3001005,
                2,
            )
            raise HttpError(400, "DB integrity error")
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Tag not created : {str(e)}",
            None,
            None,
            None,
            3001901,
            2,
        )
        raise HttpError(500, f"Record creation error : {str(e)}")


@tag_router.put("/update/{tag_id}")
def update_tag(request, tag_id: int, payload: TagIn):
    """
    The function `update_tag` updates the tag specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        tag_id (int): the id of the tag to update
        payload (TagIn): a tag object

    Returns:
        success: True

    Raises:
        Http404: If the tag with the specified ID does not exist.
    """

    try:
        tag = get_object_or_404(Tag, id=tag_id)
        maintag = None
        subtag = None
        if payload.parent_name:
            try:
                parent = MainTag.objects.create(
                    tag_name=payload.parent_name,
                    tag_type_id=payload.tag_type_id,
                )
                payload.parent_id = parent.id
            except IntegrityError as integrity_error:
                # Check if the integrity error is due to a duplicate
                if "unique constraint" in str(integrity_error).lower():
                    logToDB(
                        f"Tag not created : tag exists",
                        None,
                        None,
                        None,
                        3001004,
                        2,
                    )
                    raise HttpError(400, "Tag already exists")
                else:
                    # Log other types of integry errors
                    logToDB(
                        "Tag not created : db integrity error",
                        None,
                        None,
                        None,
                        3001005,
                        2,
                    )
                    raise HttpError(400, "DB integrity error")
            except Exception as e:
                # Log other types of exceptions
                logToDB(
                    f"Tag not created : {str(e)}",
                    None,
                    None,
                    None,
                    3001901,
                    2,
                )
                raise HttpError(500, "Record creation error")
        if payload.child_name:
            try:
                child = SubTag.objects.create(
                    tag_name=payload.child_name,
                    tag_type_id=payload.tag_type_id,
                )
                payload.child_id = child.id
            except IntegrityError as integrity_error:
                # Check if the integrity error is due to a duplicate
                if "unique constraint" in str(integrity_error).lower():
                    logToDB(
                        f"Tag not created : tag exists",
                        None,
                        None,
                        None,
                        3001004,
                        2,
                    )
                    raise HttpError(400, "Tag already exists")
                else:
                    # Log other types of integry errors
                    logToDB(
                        "Tag not created : db integrity error",
                        None,
                        None,
                        None,
                        3001005,
                        2,
                    )
                    raise HttpError(400, "DB integrity error")
            except Exception as e:
                # Log other types of exceptions
                logToDB(
                    f"Tag not created : {str(e)}",
                    None,
                    None,
                    None,
                    3001901,
                    2,
                )
                raise HttpError(500, "Record creation error")
        tag.parent_id = payload.parent_id
        tag.child_id = payload.child_id
        tag.tag_type_id = payload.tag_type_id
        tag.save()
        logToDB(
            f"Tag updated : {tag.tag_name}",
            None,
            None,
            None,
            3001002,
            1,
        )
        return {"success": True}
    except IntegrityError as integrity_error:
        # Check if the integrity error is due to a duplicate
        if "unique constraint" in str(integrity_error).lower():
            logToDB(
                f"Tag not updated : tag exists ({payload.tag_name})",
                None,
                None,
                None,
                3001004,
                2,
            )
            raise HttpError(400, "Tag already exists")
        else:
            # Log other types of integry errors
            logToDB(
                "Tag not updated : db integrity error",
                None,
                None,
                None,
                3001005,
                2,
            )
            raise HttpError(400, "DB integrity error")
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Tag not updated : {str(e)}",
            None,
            None,
            None,
            3001902,
            2,
        )
        raise HttpError(500, f"Record update error: {str(e)}")


@tag_router.get("/get/{tag_id}", response=TagOut)
def get_tag(request, tag_id: int):
    """
    The function `get_tag` retrieves the tag by id

    Args:
        request (HttpRequest): The HTTP request object.
        tag_id (int): The id of the tag to retrieve.

    Returns:
        TagOut: the tag object

    Raises:
        Http404: If the tag with the specified ID does not exist.
    """

    try:
        tag = get_object_or_404(Tag, id=tag_id)
        logToDB(
            f"Tag retrieved : {tag.tag_name}",
            None,
            None,
            None,
            3001006,
            1,
        )
        return tag
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Tag not retrieved : {str(e)}",
            None,
            None,
            None,
            3001904,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@tag_router.get("/list", response=List[TagOut])
def list_tags(
    request,
    tag_type: Optional[int] = Query(None),
    parent: Optional[int] = Query(None),
    child: Optional[int] = Query(None),
):
    """
    The function `list_tags` retrieves a list of tags,
    optionally filtered by tag type, parent, or child.

    Args:
        request (HttpRequest): The HTTP request object.
        tag_type (int): Optional tag type id to filter tags.
        parent (int): Optional filter on parent
        child (int): Optional filter on child

    Returns:
        TagOut: a list of tag objects
    """

    try:
        # Retrive a list of tags
        qs = Tag.objects.all()

        # Filter tags by tag type if a tag type is specified
        if tag_type is not None:
            qs = qs.filter(tag_type__id=tag_type)

        # Filter tags by parent if a parent id is specified
        if parent is not None:
            qs = qs.filter(parent__id=parent).exclude(tag_type__id=3)

        # Filter tags by child if a child id is specified
        if child is not None:
            qs = qs.filter(child__id=child).exclude(tag_type__id=3)

        qs = qs.annotate(
            parent_tag=F("parent__tag_name"),
            child_tag=F("child__tag_name"),
            tag_name_combined=Case(
                When(child_tag__isnull=True, then=F("parent_tag")),
                default=Concat(F("parent_tag"), Value(" / "), F("child_tag")),
                output_field=CharField(),
            ),
        )

        # Order tags by parent__tag_name, child__tag_name
        qs = qs.order_by("tag_name_combined")
        logToDB(
            "Tag list retrieved",
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
            f"Tag list not retrieved : {str(e)}",
            None,
            None,
            None,
            3001907,
            2,
        )
        raise HttpError(500, f"Record retrieval error: {str(e)}")


@tag_router.delete("/delete/{tag_id}")
def delete_tag(request, tag_id: int):
    """
    The function `delete_tag` deletes the tag specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        tag_id (int): the id of the tag to delete

    Returns:
        success: True

    Raises:
        Http404: If the tag with the specified ID does not exist.
    """

    try:
        tag = get_object_or_404(Tag, id=tag_id)
        tag_name = tag.tag_name
        tag.delete()
        logToDB(
            f"Tag deleted : {tag_name}",
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
            f"Tag not deleted : {str(e)}",
            None,
            None,
            None,
            3001903,
            2,
        )
        raise HttpError(500, "Record retrieval error")
