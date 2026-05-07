from administration.dto import (
    DomainPayee,
    DomainDescriptionHistory,
    DomainGraphType,
    DomainMessage,
    DomainMessageList,
    DomainOption,
    DomainVersion,
)
from administration.api.schemas.payee import PayeeOut
from administration.api.schemas.description_history import DescriptionHistoryOut
from administration.api.schemas.graph_type import GraphTypeOut
from administration.api.schemas.message import MessageOut, MessageList
from administration.api.schemas.option import OptionOut
from administration.api.schemas.version import VersionOut
from tags.mappers import domain_tag_to_schema


def domain_payee_to_schema(
    pay: DomainPayee,
) -> PayeeOut:
    return PayeeOut(id=pay.id, payee_name=pay.payee_name)


def domain_description_history_to_schema(
    desc: DomainDescriptionHistory,
) -> DescriptionHistoryOut:
    return DescriptionHistoryOut(
        id=desc.id,
        description_pretty=desc.description_pretty,
        tag=domain_tag_to_schema(desc.tag),
    )


def domain_graph_type_to_schema(graph_type: DomainGraphType) -> GraphTypeOut:
    if graph_type is not None:
        return GraphTypeOut(id=graph_type.id, graph_type=graph_type.graph_type)
    else:
        return None


def domain_message_to_schema(msg: DomainMessage) -> MessageOut:
    return MessageOut(
        id=msg.id,
        message_date=msg.message_date,
        message=msg.message,
        unread=msg.unread,
    )


def domain_message_list_to_schema(msg_list: DomainMessageList) -> MessageList:
    return MessageList(
        unread_count=msg_list.unread_count,
        total_count=msg_list.total_count,
        messages=[domain_message_to_schema(msg) for msg in msg_list.messages],
    )


def domain_option_to_schema(option: DomainOption) -> OptionOut:
    return OptionOut(
        id=option.id,
        alert_balance=option.alert_balance,
        alert_period=option.alert_period,
        widget1_graph_name=option.widget1_graph_name,
        widget1_month=option.widget1_month,
        widget2_graph_name=option.widget2_graph_name,
        widget2_month=option.widget2_month,
        widget3_graph_name=option.widget3_graph_name,
        widget3_month=option.widget3_month,
        widget1_tag_id=option.widget1_tag_id,
        widget1_type=domain_graph_type_to_schema(option.widget1_type),
        widget1_exclude=option.widget1_exclude,
        widget2_tag_id=option.widget2_tag_id,
        widget2_type=domain_graph_type_to_schema(option.widget2_type),
        widget2_exclude=option.widget2_exclude,
        widget3_tag_id=option.widget3_tag_id,
        widget3_type=domain_graph_type_to_schema(option.widget3_type),
        widget3_exclude=option.widget3_exclude,
        auto_archive=option.auto_archive,
        archive_length=option.archive_length,
        enable_cc_bill_calculation=option.enable_cc_bill_calculation,
        report_main=option.report_main,
        report_individual=option.report_individual,
        retirement_accounts=option.retirement_accounts,
    )


def domain_version_to_schema(ver: DomainVersion) -> VersionOut:
    return VersionOut(id=ver.id, version_number=ver.version_number)
