from tags.dto import (
    DomainTag,
    DomainMainTag,
    DomainSubTag,
    DomainTagType,
    DomainGraph,
    DomainGraphDataset,
    DomainPieGraphItem,
    DomainTagGraph,
)
from tags.api.schemas.tag import TagOut, MainTagOut, SubTagOut, TagTypeOut
from tags.api.schemas.graph_by_tags import GraphDataset, GraphOut, PieGraphItem
from tags.api.schemas.tag_graph import TagGraphOut
from accounts.mappers import domain_graph_data_to_schema
from transactions.mappers import domain_transaction_to_schema


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


def domain_graph_dataset_to_schema(ds: DomainGraphDataset) -> GraphDataset:
    return GraphDataset(
        label=ds.label,
        data=ds.data,
        backgroundColor=ds.backgroundColor,
        hoverOffset=ds.hoverOffset,
    )


def domain_graph_to_schema(graph: DomainGraph) -> GraphOut:
    return GraphOut(
        labels=graph.labels,
        datasets=[domain_graph_dataset_to_schema(gr) for gr in graph.datasets],
    )


def domain_pie_graph_item_to_schema(pie: DomainPieGraphItem) -> PieGraphItem:
    return PieGraphItem(
        key=pie.key,
        title=pie.title,
        value=pie.value,
        color=pie.color,
        total=pie.total,
    )


def domain_tag_graph_to_schema(graph: DomainTagGraph) -> TagGraphOut:
    return TagGraphOut(
        data=domain_graph_data_to_schema(graph.data),
        year1=graph.year1,
        year2=graph.year2,
        year1_avg=graph.year1_avg,
        year2_avg=graph.year2_avg,
        transactions=[
            domain_transaction_to_schema(trans) for trans in graph.transactions
        ],
    )
