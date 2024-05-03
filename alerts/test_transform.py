"""Unit tests to test transform functions"""

import pandas as pd
from pandas.testing import assert_frame_equal

from transform import process_xml, convert_timestamps
from test_data.test_vars import (OUTPUT_AFTER_PROCESSING_XML,
                                 TIMESTAMP_WITH_END_TIME,
                                 TIMESTAMP_WITHOUT_END_TIME,
                                 TIMESTAMP_OUTPUT_1,
                                 TIMESTAMP_OUTPUT_2)

UK_TIMEZONE = 'Europe/London'
NS = {"ns": "http://nationalrail.co.uk/xml/incident",
      "com": "http://nationalrail.co.uk/xml/common"}


with open("incidents/test_data/test_incident_data.xml", "r", encoding="utf-8") as file:
    MSG = file.read()


def test_process_xml_normal_input():
    """Tests the process xml function if input contains expected string."""

    processed_msg = process_xml(MSG, NS)
    assert processed_msg == OUTPUT_AFTER_PROCESSING_XML
    assert isinstance(processed_msg, dict)


def test_process_xml_bad_input():
    """Tests process xml function if input string is empty."""

    empty_msg = ''
    assert process_xml(empty_msg, NS) is None


def test_convert_timestamps_with_end_time_normal_input():
    """Tests converting timestamps with all timestamps."""

    timestamps = pd.DataFrame(TIMESTAMP_WITH_END_TIME)
    converted = convert_timestamps(
        timestamps, UK_TIMEZONE)
    expected_df = pd.DataFrame(TIMESTAMP_OUTPUT_1)
    assert_frame_equal(converted, expected_df)


def test_convert_timestamps_without_end_time_normal_input():
    """Tests converting timestamps without end time."""

    timestamps = pd.DataFrame(TIMESTAMP_WITHOUT_END_TIME)
    converted = convert_timestamps(timestamps, UK_TIMEZONE)
    expected_df = pd.DataFrame(TIMESTAMP_OUTPUT_2)
    assert_frame_equal(converted, expected_df)
