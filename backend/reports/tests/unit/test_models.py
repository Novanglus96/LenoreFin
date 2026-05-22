import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from reports.models import ReportConfig, ReportConfigTag


@pytest.fixture
def basic_config(db):
    return ReportConfig.objects.create(
        name="Test Report",
        report_type="TOTALS",
        date_range_type="THIS_YEAR",
        group_by="TAG",
    )


@pytest.mark.django_db
@pytest.mark.unit
class TestReportConfig:
    def test_create_minimal(self):
        config = ReportConfig.objects.create(
            name="My Report",
            report_type="TOTALS",
            date_range_type="THIS_YEAR",
            group_by="TAG",
        )
        assert config.id is not None
        assert config.show_transactions is False
        assert config.show_subtotal is True
        assert config.include_pending is False
        assert config.description == ""

    def test_str(self, basic_config):
        assert str(basic_config) == "Test Report"

    def test_ordering_by_updated_at_desc(self, db):
        ReportConfig.objects.create(name="First", report_type="TOTALS", date_range_type="THIS_YEAR", group_by="TAG")
        ReportConfig.objects.create(name="Second", report_type="TOTALS", date_range_type="THIS_YEAR", group_by="TAG")
        names = list(ReportConfig.objects.values_list("name", flat=True))
        assert names[0] == "Second"
        assert names[1] == "First"

    def test_defaults(self, basic_config):
        assert basic_config.date_from is None
        assert basic_config.date_to is None
        assert basic_config.created_at is not None
        assert basic_config.updated_at is not None


@pytest.mark.django_db
@pytest.mark.unit
class TestReportConfigTag:
    def test_tag_only(self, basic_config, test_tag):
        sel = ReportConfigTag.objects.create(report=basic_config, tag=test_tag)
        assert sel.tag_id == test_tag.id
        assert sel.sub_tag_id is None
        assert sel.main_tag_id is None

    def test_sub_tag_only(self, basic_config, test_sub_tag):
        sel = ReportConfigTag.objects.create(report=basic_config, sub_tag=test_sub_tag)
        assert sel.sub_tag_id == test_sub_tag.id
        assert sel.tag_id is None
        assert sel.main_tag_id is None

    def test_main_tag_only(self, basic_config, test_main_tag):
        sel = ReportConfigTag.objects.create(report=basic_config, main_tag=test_main_tag)
        assert sel.main_tag_id == test_main_tag.id
        assert sel.tag_id is None
        assert sel.sub_tag_id is None

    def test_clean_rejects_none_set(self, basic_config):
        sel = ReportConfigTag(report=basic_config)
        with pytest.raises(ValidationError):
            sel.clean()

    def test_clean_rejects_two_set(self, basic_config, test_tag, test_sub_tag):
        sel = ReportConfigTag(report=basic_config, tag=test_tag, sub_tag=test_sub_tag)
        with pytest.raises(ValidationError):
            sel.clean()

    def test_clean_rejects_all_three_set(self, basic_config, test_tag, test_sub_tag, test_main_tag):
        sel = ReportConfigTag(report=basic_config, tag=test_tag, sub_tag=test_sub_tag, main_tag=test_main_tag)
        with pytest.raises(ValidationError):
            sel.clean()

    def test_db_constraint_rejects_none_set(self, basic_config):
        with pytest.raises(IntegrityError):
            ReportConfigTag.objects.create(report=basic_config)

    def test_cascade_delete_on_report_delete(self, basic_config, test_tag):
        sel = ReportConfigTag.objects.create(report=basic_config, tag=test_tag)
        config_id = basic_config.id
        sel_id = sel.id
        basic_config.delete()
        assert not ReportConfigTag.objects.filter(id=sel_id).exists()
        assert not ReportConfig.objects.filter(id=config_id).exists()

    def test_str_tag(self, basic_config, test_tag):
        sel = ReportConfigTag(report=basic_config, tag_id=test_tag.id)
        assert "Tag:" in str(sel)

    def test_str_sub_tag(self, basic_config, test_sub_tag):
        sel = ReportConfigTag(report=basic_config, sub_tag_id=test_sub_tag.id)
        assert "SubTag:" in str(sel)

    def test_str_main_tag(self, basic_config, test_main_tag):
        sel = ReportConfigTag(report=basic_config, main_tag_id=test_main_tag.id)
        assert "MainTag:" in str(sel)
