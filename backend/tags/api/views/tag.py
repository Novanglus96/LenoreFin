from ninja import Router, Query
from ninja.errors import HttpError
from tags.models import Tag
from tags.api.schemas.tag import TagIn, TagOut, TagQuery
from django.shortcuts import get_object_or_404
from django.db.models import (
    Case,
    When,
    Value,
    F,
    CharField,
)
from django.db.models.functions import Concat
from typing import List
from tags.services import create_tag, update_tag, TagAlreadyExists, TagNotFound, InvalidTagData
import logging

api_logger = logging.getLogger("api")
error_logger = logging.getLogger("error")

tag_router = Router(tags=["Tags"])


@tag_router.post("/create")
def create_tag_view(request, payload: TagIn):
    try:
        tag_id = create_tag(
            parent_id=payload.parent_id,
            parent_name=payload.parent_name,
            child_id=payload.child_id,
            child_name=payload.child_name,
            tag_type_id=payload.tag_type_id,
        )
        api_logger.info(f"Tag created : id={tag_id}")
        return {"id": tag_id}
    except TagAlreadyExists as e:
        api_logger.error(f"Tag not created : {e}")
        error_logger.error(str(e))
        raise HttpError(400, "Tag already exists")
    except InvalidTagData as e:
        api_logger.error(f"Tag not created : {e}")
        error_logger.error(str(e))
        raise HttpError(500, "Invalid tag data")
    except Exception as e:
        api_logger.error("Tag not created")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, f"Record creation error : {str(e)}")


@tag_router.put("/update/{tag_id}")
def update_tag_view(request, tag_id: int, payload: TagIn):
    try:
        update_tag(
            tag_id=tag_id,
            parent_id=payload.parent_id,
            parent_name=payload.parent_name,
            child_id=payload.child_id,
            child_name=payload.child_name,
            tag_type_id=payload.tag_type_id,
        )
        api_logger.info(f"Tag updated : id={tag_id}")
        return {"success": True}
    except TagNotFound:
        raise HttpError(404, "Tag not found")
    except TagAlreadyExists as e:
        api_logger.error(f"Tag not updated : {e}")
        error_logger.error(str(e))
        raise HttpError(400, "Tag already exists")
    except Exception as e:
        api_logger.error("Tag not updated")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, f"Record update error: {str(e)}")


@tag_router.get("/get/{tag_id}", response=TagOut)
def get_tag(request, tag_id: int):
    try:
        tag = get_object_or_404(Tag, id=tag_id)
        api_logger.debug(f"Tag retrieved : {tag.tag_name}")
        return tag
    except Exception as e:
        api_logger.error("Tag not retrieved")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record retrieval error")


@tag_router.get("/list", response=List[TagOut])
def list_tags(request, query: TagQuery = Query(...)):
    try:
        qs = Tag.objects.all()

        if query.tag_type is not None:
            qs = qs.filter(tag_type__id=query.tag_type)
        if query.parent is not None:
            qs = qs.filter(parent__id=query.parent).exclude(tag_type__id=3)
        if query.child is not None:
            qs = qs.filter(child__id=query.child).exclude(tag_type__id=3)
        if query.main_only:
            qs = qs.filter(child__isnull=True)

        qs = qs.annotate(
            parent_tag=F("parent__tag_name"),
            child_tag=F("child__tag_name"),
            tag_name_combined=Case(
                When(child_tag__isnull=True, then=F("parent_tag")),
                default=Concat(F("parent_tag"), Value(" / "), F("child_tag")),
                output_field=CharField(),
            ),
        ).order_by("tag_name_combined")

        api_logger.debug("Tag list retrieved")
        return qs
    except Exception as e:
        api_logger.error("Tag list not retrieved")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, f"Record retrieval error: {str(e)}")


@tag_router.delete("/delete/{tag_id}")
def delete_tag(request, tag_id: int):
    try:
        tag = get_object_or_404(Tag, id=tag_id)
        tag_name = tag.tag_name
        tag.delete()
        api_logger.info(f"Tag deleted : {tag_name}")
        return {"success": True}
    except Exception as e:
        api_logger.error("Tag not deleted")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record retrieval error")
