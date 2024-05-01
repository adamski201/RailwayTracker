import pytest
from performance_transform import get_datetime_from_time_str
from datetime import date, datetime


def test_get_datetime_from_time_str():
    test_date = date(2024, 4, 30)
    test_time_str = "0830"

    result = get_datetime_from_time_str(test_date, test_time_str)

    expected_result = datetime(2024, 4, 30, 8, 30)

    assert result == expected_result
