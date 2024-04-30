"""Functions to transform and clean messages upon receipt"""

from datetime import datetime

import xml.etree.ElementTree as ET

import pandas as pd
from bs4 import BeautifulSoup


UK_TIMEZONE = 'Europe/London'
CURRENT_TIME = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f%z")


def find_element_text(root: ET.Element, xpath: str, namespaces: dict) -> str:
    """Returns text if element text exists."""

    element = root.find(xpath, namespaces)
    return element.text if element is not None else None


def extract_operator_refs(root: ET.Element, namespaces: dict) -> list[str]:
    """Returns list of all operator codes."""

    operator_refs = [operator_ref.text for operator_ref in root.findall(
        ".//ns:Affects/ns:Operators/ns:AffectedOperator/ns:OperatorRef", namespaces)]
    return operator_refs


def extract_operator_names(root: ET.Element, namespaces: dict) -> list[str]:
    """Returns list of all operators names"""

    operator_names = [operator_name.text for operator_name in root.findall(
        ".//ns:Affects/ns:Operators/ns:AffectedOperator/ns:OperatorName", namespaces)]
    return operator_names


def process_xml(xml_message: str, namespaces: dict) -> dict:
    """Processes each XML message to extract relevant information."""

    if not xml_message:
        return None

    root = ET.fromstring(xml_message)
    created_at = find_element_text(root, ".//ns:CreationTime", namespaces)
    last_updated = find_element_text(
        root, ".//com:LastChangedDate", namespaces)
    incident_num = find_element_text(root, ".//ns:IncidentNumber", namespaces)
    start_time = find_element_text(root, ".//com:StartTime", namespaces)
    end_time = find_element_text(root, ".//com:EndTime", namespaces)
    planned = find_element_text(root, ".//ns:Planned", namespaces)
    summary = find_element_text(root, ".//ns:Summary", namespaces)
    cleared = find_element_text(root, ".//ns:ClearedIncident", namespaces)
    info_link = find_element_text(
        root, ".//ns:InfoLinks/ns:InfoLink/ns:Uri", namespaces).replace('/n', " ").strip()
    operator_ref = extract_operator_refs(root, namespaces)
    operator_name = extract_operator_names(root, namespaces)
    routes_affected = find_element_text(
        root, ".//ns:Affects/ns:RoutesAffected", namespaces)
    incident_priority = find_element_text(
        root, ".//ns:IncidentPriority", namespaces)
    if routes_affected:
        routes_affected = routes_affected.replace(
            "\n", " ").replace("</p><p>", "\n")
        routes_soup = BeautifulSoup(routes_affected, "html.parser").get_text()
    else:
        routes_soup = None

    if not cleared and end_time:
        cleared = CURRENT_TIME > end_time

    data = {
        "created_at": created_at,
        "last_updated": last_updated,
        "operator_ref": operator_ref,
        "operator_name": operator_name,
        "incident_number": incident_num,
        "start_time": start_time,
        "end_time": end_time,
        "planned": planned,
        "cleared": cleared,
        "info_link": info_link,
        "routes_affected": routes_soup,
        "incident_priority": incident_priority,
        "summary": summary
    }

    return data


def convert_timestamps(data_frame: pd.DataFrame, timezone: str) -> pd.DataFrame:
    """Converts timestamp to correct datetime format with correct time zone."""

    columns_to_convert = ['created_at', 'last_updated',
                          'start_time', 'end_time']

    for col in columns_to_convert:
        if data_frame[col].notnull().any():
            data_frame[col] = pd.to_datetime(data_frame[col])
            data_frame[col] = data_frame[col].dt.tz_convert(tz=timezone)

    return data_frame


def transform_data(message: str, namespaces: dict):
    """Transforms/cleans each message."""

    data = process_xml(message, namespaces)
    data_frame = pd.DataFrame([data])
    data_frame = convert_timestamps(data_frame, UK_TIMEZONE)
    return data_frame.to_dict(orient='records')[0]
