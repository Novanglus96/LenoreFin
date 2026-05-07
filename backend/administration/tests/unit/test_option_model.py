import pytest
from administration.models import Option, GraphType
from django.core.exceptions import ValidationError


@pytest.mark.django_db
def test_option_creation():
    graph_type = GraphType.objects.create(graph_type="Graph Type")
    option = Option.objects.create(
        alert_balance=0.00,
        alert_period=3,
        widget1_graph_name="Graph1",
        widget1_tag_id=1,
        widget1_type=graph_type,
        widget1_month=1,
        widget1_exclude="",
        widget2_graph_name="Graph2",
        widget2_tag_id=1,
        widget2_type=graph_type,
        widget2_month=1,
        widget2_exclude="",
        widget3_graph_name="Graph3",
        widget3_tag_id=1,
        widget3_type=graph_type,
        widget3_month=1,
        widget3_exclude="",
        auto_archive=True,
        archive_length=2,
        enable_cc_bill_calculation=True,
        report_main="Main Report",
        report_individual="Individual Report",
        retirement_accounts=None,
        christmas_accounts=None,
        christmas_rewards=None,
    )

    assert option.alert_balance == 0.00
    assert option.alert_period == 3
    assert option.widget1_graph_name == "Graph1"
    assert option.widget1_tag_id == 1
    assert option.widget1_type == graph_type
    assert option.widget1_month == 1
    assert option.widget1_exclude == ""
    assert option.widget2_graph_name == "Graph2"
    assert option.widget2_tag_id == 1
    assert option.widget2_type == graph_type
    assert option.widget2_month == 1
    assert option.widget2_exclude == ""
    assert option.widget3_graph_name == "Graph3"
    assert option.widget3_tag_id == 1
    assert option.widget3_type == graph_type
    assert option.widget3_month == 1
    assert option.widget3_exclude == ""
    assert option.auto_archive
    assert option.archive_length == 2
    assert option.enable_cc_bill_calculation
    assert option.report_main == "Main Report"
    assert option.report_individual == "Individual Report"
    assert option.retirement_accounts is None
    assert option.christmas_accounts is None
    assert option.christmas_rewards is None


@pytest.mark.django_db
def test_option_defaults():
    option = Option.objects.create(
        widget1_graph_name="Graph1",
        widget1_exclude="",
        widget2_graph_name="Graph2",
        widget2_exclude="",
        widget3_graph_name="Graph3",
        widget3_exclude="",
    )

    assert option.alert_balance == 0.00
    assert option.alert_period == 3
    assert option.widget1_tag_id is None
    assert option.widget1_type is None
    assert option.widget1_month == 0
    assert option.widget2_tag_id is None
    assert option.widget2_type is None
    assert option.widget2_month == 0
    assert option.widget3_tag_id is None
    assert option.widget3_type is None
    assert option.widget3_month == 0
    assert option.auto_archive
    assert option.archive_length == 2
    assert option.enable_cc_bill_calculation
    assert option.report_main is None
    assert option.report_individual is None
    assert option.retirement_accounts is None
    assert option.christmas_accounts is None
    assert option.christmas_rewards is None


@pytest.mark.django_db
def test_option_singleton_prevents_second_instance():
    graph_type = GraphType.objects.create(graph_type="Graph Type")
    Option.objects.create(
        alert_balance=0.00,
        alert_period=3,
        widget1_graph_name="Graph1",
        widget1_tag_id=1,
        widget1_type=graph_type,
        widget1_month=1,
        widget1_exclude="",
        widget2_graph_name="Graph2",
        widget2_tag_id=1,
        widget2_type=graph_type,
        widget2_month=1,
        widget2_exclude="",
        widget3_graph_name="Graph3",
        widget3_tag_id=1,
        widget3_type=graph_type,
        widget3_month=1,
        widget3_exclude="",
        auto_archive=True,
        archive_length=2,
        enable_cc_bill_calculation=True,
        report_main="Main Report",
        report_individual="Individual Report",
        retirement_accounts=None,
        christmas_accounts=None,
        christmas_rewards=None,
    )

    with pytest.raises(ValidationError) as exc:
        Option.objects.create(
            alert_balance=0.00,
            alert_period=3,
            widget1_graph_name="Graph1",
            widget1_tag_id=1,
            widget1_type=graph_type,
            widget1_month=1,
            widget1_exclude="",
            widget2_graph_name="Graph2",
            widget2_tag_id=1,
            widget2_type=graph_type,
            widget2_month=1,
            widget2_exclude="",
            widget3_graph_name="Graph3",
            widget3_tag_id=1,
            widget3_type=graph_type,
            widget3_month=1,
            widget3_exclude="",
            auto_archive=True,
            archive_length=2,
            enable_cc_bill_calculation=True,
            report_main="Main Report",
            report_individual="Individual Report",
            retirement_accounts=None,
            christmas_accounts=None,
            christmas_rewards=None,
        )

    assert "already one instance" in str(exc.value)


@pytest.mark.django_db
def test_option_singleton_cannot_be_deleted():
    graph_type = GraphType.objects.create(graph_type="Graph Type")
    option = Option.objects.create(
        alert_balance=0.00,
        alert_period=3,
        widget1_graph_name="Graph1",
        widget1_tag_id=1,
        widget1_type=graph_type,
        widget1_month=1,
        widget1_exclude="",
        widget2_graph_name="Graph2",
        widget2_tag_id=1,
        widget2_type=graph_type,
        widget2_month=1,
        widget2_exclude="",
        widget3_graph_name="Graph3",
        widget3_tag_id=1,
        widget3_type=graph_type,
        widget3_month=1,
        widget3_exclude="",
        auto_archive=True,
        archive_length=2,
        enable_cc_bill_calculation=True,
        report_main="Main Report",
        report_individual="Individual Report",
        retirement_accounts=None,
        christmas_accounts=None,
        christmas_rewards=None,
    )

    with pytest.raises(ValidationError):
        option.delete()
