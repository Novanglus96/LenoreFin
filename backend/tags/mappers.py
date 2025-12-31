from tags.dto import DomainTag, DomainMainTag, DomainSubTag, DomainTagType
from tags.api.schemas.tag import TagOut, MainTagOut, SubTagOut, TagTypeOut


def domain_tag_type_to_schema(
    type: DomainTagType,
) -> TagTypeOut:
    return TagTypeOut(id=type.id, tag_type=type.tag_type)


def domain_main_tag_to_schema(
    tag: DomainMainTag,
) -> MainTagOut:
    return MainTagOut(
        id=tag.id,
        tag_name=tag.tag_name,
        tag_type=domain_tag_type_to_schema(tag.tag_type),
    )


def domain_sub_tag_to_schema(
    tag: DomainSubTag,
) -> SubTagOut:
    return SubTagOut(
        id=tag.id,
        tag_name=tag.tag_name,
        tag_type=domain_tag_type_to_schema(tag.tag_type),
    )


def domain_tag_to_schema(
    tag: DomainTag,
) -> TagOut:
    return TagOut(
        id=tag.id,
        tag_name=tag.tag_name,
        parent=domain_main_tag_to_schema(tag.parent),
        child=domain_sub_tag_to_schema(tag.child) if tag.child else None,
        tag_type=tag.tag_type,
    )
