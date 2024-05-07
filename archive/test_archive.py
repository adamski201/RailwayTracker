"""Tests for the archive module."""

import pandas as pd

from archive import convert_to_list


def test_convert_to_list_non_empty_df():
    """Tests that `convert_to_list` correctly converts a DataFrame 
    with non-empty data into a list of tuples."""

    data = pd.DataFrame({
        'col1': [1, 2, 3],
        'col2': ['a', 'b', 'c']
    })

    result = convert_to_list(data)

    expected_result = [(1, 'a'), (2, 'b'), (3, 'c')]
    assert result == expected_result


def test_convert_to_list_mixed_data_types():
    """Tests that `convert_to_list` handles DataFrame with mixed data types 
    by converting it into a list of tuples whilst preserving the data types."""

    data = pd.DataFrame({
        'col1': [1, 2, 3],
        'col2': ['a', 'b', 'c'],
        'col3': [1.1, 2.2, 3.3]
    })

    result = convert_to_list(data)

    expected_result = [(1, 'a', 1.1), (2, 'b', 2.2), (3, 'c', 3.3)]
    assert result == expected_result
