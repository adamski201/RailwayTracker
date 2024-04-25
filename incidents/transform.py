"""Functions to transform and clean extracted data"""
import xml.etree.ElementTree as ET

import pandas as pd
from bs4 import BeautifulSoup

UK_TIMEZONE = 'Europe/London'

ns = {"ns": "http://nationalrail.co.uk/xml/incident",
      "com": "http://nationalrail.co.uk/xml/common"}


def process_xml(xml_message: str) -> list[dict]:
    """Processes each xml message to extract relevant information"""
    
    if xml_message:
        root = ET.fromstring(xml_message)
        created_at = root.find(".//ns:CreationTime", ns).text
        last_updated = root.find(".//com:LastChangedDate", ns).text
        incident_num = root.find(".//ns:IncidentNumber", ns).text
        start_time = root.find(".//com:StartTime", ns).text
        end_time = root.find(".//com:EndTime", ns)
        planned = root.find(".//ns:Planned", ns).text
        summary = root.find(".//ns:Summary", ns).text
        description = root.find(".//ns:Description", ns).text
        info_link = root.find(".//ns:InfoLinks/ns:InfoLink/ns:Uri", ns).text
        operator_ref = root.find(
            ".//ns:Affects/ns:Operators/ns:AffectedOperator/ns:OperatorRef", ns).text
        operator_name = root.find(
            ".//ns:Affects/ns:Operators/ns:AffectedOperator/ns:OperatorName", ns).text
        routes_affected = root.find(
            ".//ns:Affects/ns:RoutesAffected", ns).text
        incident_priority = root.find(".//ns:IncidentPriority", ns).text
        end_time = end_time.text if end_time is not None else None
        description_soup = BeautifulSoup(
            description, "html.parser").get_text(separator='\n').replace('\u200b', '')
        routes_soup = BeautifulSoup(
            routes_affected, "html.parser").get_text()

        data = [{
            "created_at": created_at,
            "last_updated": last_updated,
            "operator_ref": operator_ref,
            "operator_name": operator_name,
            "incident_number": incident_num,
            "start_time": start_time,
            "end_time": end_time,
            "planned": planned,
            "info_link": info_link,
            "routes_affected": routes_soup,
            "incident_priority": incident_priority,
            "summary": summary,
            "description": description_soup,

        }]

        return data
    return None


def replace_new_line(df: pd.DataFrame) -> pd.DataFrame:
    """Replaces new line characters in description and routes affected"""

    df['description'] = df['description'].str.replace('\n', ' ')
    df['routes_affected'] = df['routes_affected'].str.replace('\n', ' ')
    return df


def convert_timestamps(df: pd.DataFrame, timezone: str) -> pd.DataFrame:
    """Converts timestamp to correct datetime format with correct time zone"""

    columns_to_convert = ['created_at', 'last_updated',
                          'start_time', 'end_time']

    for col in columns_to_convert:
        if df[col].notnull().any():
            df[col] = pd.to_datetime(df[col])
            df[col] = df[col].dt.tz_convert(tz=timezone)

    return df


def transform_message(message):
    """Transforms/cleans each message"""

    data = process_xml(message)
    data_frame = pd.DataFrame(data)
    data_frame = convert_timestamps(replace_new_line(data_frame), UK_TIMEZONE)
    return data_frame.to_dict(orient='records')
