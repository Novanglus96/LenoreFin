import pytest
from datetime import date
from unittest.mock import patch

from reports.services.execution import compute_date_range


def _patch_today(d: date):
    return patch("reports.services.execution.date")


@pytest.mark.unit
class TestComputeDateRange:
    def _today(self, d: date):
        return patch("reports.services.execution.date", wraps=date, **{"today.return_value": d})

    def test_this_year(self):
        with self._today(date(2026, 5, 19)):
            start, end = compute_date_range("THIS_YEAR")
        assert start == date(2026, 1, 1)
        assert end == date(2026, 12, 31)

    def test_last_year(self):
        with self._today(date(2026, 5, 19)):
            start, end = compute_date_range("LAST_YEAR")
        assert start == date(2025, 1, 1)
        assert end == date(2025, 12, 31)

    def test_this_quarter_q1(self):
        with self._today(date(2026, 2, 15)):
            start, end = compute_date_range("THIS_QUARTER")
        assert start == date(2026, 1, 1)
        assert end == date(2026, 3, 31)

    def test_this_quarter_q2(self):
        with self._today(date(2026, 5, 19)):
            start, end = compute_date_range("THIS_QUARTER")
        assert start == date(2026, 4, 1)
        assert end == date(2026, 6, 30)

    def test_this_quarter_q3(self):
        with self._today(date(2026, 8, 1)):
            start, end = compute_date_range("THIS_QUARTER")
        assert start == date(2026, 7, 1)
        assert end == date(2026, 9, 30)

    def test_this_quarter_q4(self):
        with self._today(date(2026, 11, 1)):
            start, end = compute_date_range("THIS_QUARTER")
        assert start == date(2026, 10, 1)
        assert end == date(2026, 12, 31)

    def test_last_quarter_from_q2(self):
        with self._today(date(2026, 5, 19)):
            start, end = compute_date_range("LAST_QUARTER")
        assert start == date(2026, 1, 1)
        assert end == date(2026, 3, 31)

    def test_last_quarter_from_q1_crosses_year(self):
        with self._today(date(2026, 1, 15)):
            start, end = compute_date_range("LAST_QUARTER")
        assert start == date(2025, 10, 1)
        assert end == date(2025, 12, 31)

    def test_trailing_12(self):
        with self._today(date(2026, 5, 19)):
            start, end = compute_date_range("TRAILING_12")
        assert start == date(2025, 5, 20)
        assert end == date(2026, 5, 19)

    def test_custom_passthrough(self):
        start, end = compute_date_range(
            "CUSTOM", date_from=date(2024, 3, 1), date_to=date(2024, 3, 31)
        )
        assert start == date(2024, 3, 1)
        assert end == date(2024, 3, 31)

    def test_prior_year_shift(self):
        from reports.services.execution import _shift_back_one_year
        s, e = _shift_back_one_year(date(2026, 1, 1), date(2026, 12, 31))
        assert s == date(2025, 1, 1)
        assert e == date(2025, 12, 31)

    def test_prior_year_shift_custom_range(self):
        from reports.services.execution import _shift_back_one_year
        s, e = _shift_back_one_year(date(2025, 3, 1), date(2025, 3, 31))
        assert s == date(2024, 3, 1)
        assert e == date(2024, 3, 31)
