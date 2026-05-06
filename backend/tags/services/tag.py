from django.db import IntegrityError
from tags.models import Tag, MainTag, SubTag


class TagAlreadyExists(Exception):
    pass


class TagNotFound(Exception):
    pass


class InvalidTagData(Exception):
    pass


def _resolve_parent(parent_name: str, parent_id: int, tag_type_id: int) -> int:
    if not parent_name:
        return parent_id
    try:
        parent = MainTag.objects.create(
            tag_name=parent_name,
            tag_type_id=tag_type_id,
        )
        return parent.id
    except IntegrityError as e:
        if "unique constraint" in str(e).lower():
            raise TagAlreadyExists("Tag already exists")
        raise


def _resolve_child_for_create(child_name: str, child_id: int, tag_type_id: int) -> int:
    if not child_name:
        return child_id
    existing = SubTag.objects.filter(tag_name=child_name).first()
    if existing:
        return existing.id
    try:
        child = SubTag.objects.create(
            tag_name=child_name,
            tag_type_id=tag_type_id,
        )
        return child.id
    except IntegrityError as e:
        if "unique constraint" in str(e).lower():
            raise TagAlreadyExists("Tag already exists")
        raise


def _resolve_child_for_update(child_name: str, child_id: int, tag_type_id: int) -> int:
    if not child_name:
        return child_id
    try:
        child = SubTag.objects.create(
            tag_name=child_name,
            tag_type_id=tag_type_id,
        )
        return child.id
    except IntegrityError as e:
        if "unique constraint" in str(e).lower():
            raise TagAlreadyExists("Tag already exists")
        raise


def create_tag(
    parent_id: int,
    parent_name: str,
    child_id: int,
    child_name: str,
    tag_type_id: int,
) -> int:
    resolved_parent_id = _resolve_parent(parent_name, parent_id, tag_type_id)
    resolved_child_id = _resolve_child_for_create(child_name, child_id, tag_type_id)

    if not (parent_name or (child_name and resolved_parent_id)):
        raise InvalidTagData("Invalid tag data")

    try:
        tag = Tag.objects.create(
            parent_id=resolved_parent_id,
            child_id=resolved_child_id,
            tag_type_id=tag_type_id,
        )
        return tag.id
    except IntegrityError as e:
        if "unique constraint" in str(e).lower():
            raise TagAlreadyExists("Tag already exists")
        raise


def update_tag(
    tag_id: int,
    parent_id: int,
    parent_name: str,
    child_id: int,
    child_name: str,
    tag_type_id: int,
) -> None:
    try:
        tag = Tag.objects.get(id=tag_id)
    except Tag.DoesNotExist:
        raise TagNotFound(f"Tag {tag_id} not found")

    resolved_parent_id = _resolve_parent(parent_name, parent_id, tag_type_id)
    resolved_child_id = _resolve_child_for_update(child_name, child_id, tag_type_id)

    tag.parent_id = resolved_parent_id
    tag.child_id = resolved_child_id
    tag.tag_type_id = tag_type_id
    try:
        tag.save()
    except IntegrityError as e:
        if "unique constraint" in str(e).lower():
            raise TagAlreadyExists("Tag already exists")
        raise
