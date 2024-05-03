"""Functions to publish sms and email messages to SNS topic with attributes attached"""

import json
import logging

from botocore.client import BaseClient, ClientError


OPERATORS = {'VT': 'Avanti West Coast',
             'CC': 'c2c',
             'CS': 'Caledonian Sleeper',
             'CH': 'Chiltern Railways',
             'XC': 'CrossCountry',
             'EM': 'East Midlands Railway',
             'XR': 'Elizabeth Line',
             'ES': 'Eurostar',
             'GC': 'Grand Central',
             'LF': 'Grand Union Trains',
             'GN': 'Great Nothern',
             'GW': 'Great Western Railway',
             'LE': 'Greater Anglia',
             'HX': 'Heathrow Express',
             'HT': 'Hull Trains',
             'IL': 'Island Lines',
             'LO': 'London Overground',
             'LT': 'London Underground',
             'LN': 'London Northwestern Railway',
             'GR': 'LNER',
             'LD': 'Lumo',
             'ME': 'Merseyrail',
             'NT': 'Northern Trains',
             'SR': 'ScotRail',
             'SE': 'Southeastern',
             'SN': 'Southern',
             'SW': 'South Western Railway',
             'SP': 'Swanage Railway',
             'SX': 'Stansted Express',
             'TP': 'TransPennine Express',
             'AW': 'Transport for Wales',
             'TL': 'Thameslink',
             'WR': 'West Coast Railways',
             'LM': 'West Midlands Trains',
             'GX': 'Gatwick Express',
             'WM': 'West Midlands Railway'}


def convert_toc_code_to_name(toc_code: list[str]) -> list[str]:
    """Takes in a list of operator codes
    and returns list of operator names."""

    return [OPERATORS.get(code, " ") for code in toc_code]


def get_message_attributes(operators: list) -> dict:
    """Takes in a list of operator names and
      appends to the message attributes dictionary."""

    message_attributes = {}

    message_attributes['operators'] = {
        "DataType": "String.Array",
        "StringValue": json.dumps(operators)
    }
    return message_attributes


def publish_multi_message_with_attributes(sns_client: BaseClient, topic_arn: str,
                                          message_subject: str, sms_message: str,
                                          email_message: str, message_attributes: dict):
    """Publishes a multi-format message with attributes to a topic."""

    try:
        message = {
            "default": "default message",
            "sms": sms_message,
            "email": email_message,
        }

        response = sns_client.publish(
            TopicArn=topic_arn,
            Message=json.dumps(message),
            MessageAttributes=message_attributes,
            Subject=message_subject,
            MessageStructure="json"
        )
        message_id = response["MessageId"]

        logging.info(
            "Published multi-format message to topic %s.", topic_arn)

    except ClientError:

        logging.exception(
            "Couldn't publish message to topic %s.", topic_arn)
        raise
    return message_id


def create_message(data: dict, operator_list: list) -> str:
    """Creates email/sms message format."""

    summary = data["summary"]
    info_link = data["info_link"]
    routes_affected = data["routes_affected"]
    formatted_message = (
        f"RailWatch"
        f"\n\nInformation:\n{summary}\n\n"
        f"Affected operator/s:\n{', '.join(operator_list)}\n\n"
        f"Routes affected:\n{routes_affected}\n\n"
        f"Get more information at:\n{info_link}\n"
    )
    return formatted_message


def create_subject(data: dict, operator_list: list) -> str:
    """Creates subject title for notifications."""

    summary = data['summary'].lower()
    operators = ", ".join(operator_list)

    prefix_messages = {
        "lines reopened": f"RailWatch - Incident Update ({operators})",
        "amend": f"RailWatch - Amendments ({operators})",
        "alteration": f"RailWatch - Amendments ({operators})",
        "bus": f"RailWatch - Bus replacements ({operators})",
        "reduced": f"RailWatch - Reduced service ({operators})",
        "industrial action": f"RailWatch - Industrial action ({operators})"
    }
    for prefix in prefix_messages:
        if summary.startswith(prefix):
            return prefix_messages.get(prefix)

    return f"RailWatch - Incident Notice ({operators})"


def send_alerts(sns_client: BaseClient, data: dict, topic: str) -> None:
    """Processes data and publishes message to topic which triggers
      alerts to be sent to subscribers via email or/and sms."""

    operators = convert_toc_code_to_name(data["operator_ref"])
    subject = create_subject(data, operators)
    msg = create_message(data, operators)
    attributes = get_message_attributes(operators)
    publish_multi_message_with_attributes(
        sns_client, topic, subject, msg, msg, attributes)
