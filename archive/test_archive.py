"""Tests for the archive module."""

import pandas as pd

from archive import convert_to_list


def test_convert_to_list_non_empty_df():
    """Test case where DataFrame has non-empty data."""

    data = pd.DataFrame({
        'col1': [1, 2, 3],
        'col2': ['a', 'b', 'c']
    })

    result = convert_to_list(data)

    expected_result = [(1, 'a'), (2, 'b'), (3, 'c')]
    assert result == expected_result


def test_convert_to_list_mixed_data_types():
    """Test case where DataFrame has mixed data types."""

    data = pd.DataFrame({
        'col1': [1, 2, 3],
        'col2': ['a', 'b', 'c'],
        'col3': [1.1, 2.2, 3.3]
    })

    result = convert_to_list(data)

    expected_result = [(1, 'a', 1.1), (2, 'b', 2.2), (3, 'c', 3.3)]
    assert result == expected_result
