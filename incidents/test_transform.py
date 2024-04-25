"""Unit tests to test transform functions"""
import pandas as pd

from transform import process_xml, replace_new_line, convert_timestamps
from test_data.test_vars import (OUTPUT_AFTER_PROCESSING_XML,
                                 OUTPUT_AFTER_REPLACE,
                                 TIMESTAMP_WITH_END_TIME,
                                 TIMESTAMP_WITHOUT_END_TIME,
                                 TIMESTAMP_OUTPUT_1,
                                 TIMESTAMP_OUTPUT_2)

UK_TIMEZONE = 'Europe/London'

with open("test_data/test_incident_data.xml", "r", encoding="utf-8") as file:
    MSG = file.read()


def test_process_xml_normal_input():
    """tests process xml function if normal input string"""

    processed_msg = process_xml(MSG)
    assert processed_msg == OUTPUT_AFTER_PROCESSING_XML
    assert isinstance(processed_msg, list)


def test_process_xml_bad_input():
    """tests process xml function if empty input string"""

    empty_msg = ''
    assert process_xml(empty_msg) is None


def test_replace_new_line():
    """Tests replace new line character function"""

    processed_msg = process_xml(MSG)
    data_frame = pd.DataFrame(processed_msg)
    formatted_msg = replace_new_line(data_frame).to_dict(orient='list')
    assert formatted_msg == OUTPUT_AFTER_REPLACE


def test_convert_timestamps_with_end_time():
    """Tests converting timestamps with all timestamps"""

    timestamps = pd.DataFrame(TIMESTAMP_WITH_END_TIME)
    converted = convert_timestamps(
        timestamps, UK_TIMEZONE).to_dict(orient='list')
    assert converted == TIMESTAMP_OUTPUT_1


def test_convert_timestamps_without_end_time():
    """Tests converting timestamps without end time"""

    timestamps = pd.DataFrame(TIMESTAMP_WITHOUT_END_TIME)
    converted = convert_timestamps(
        timestamps, UK_TIMEZONE).to_dict(orient='list')
    assert converted == TIMESTAMP_OUTPUT_2
