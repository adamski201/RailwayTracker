"""SNS functions to allow subscriptions to an SNS topic by email or by sms."""

import json

from botocore.client import BaseClient
import streamlit as st


def convert_operators_to_ui(selected_operators: list, operator_dict: dict) -> list:
    """Returns unique identifiers for a given operator list."""

    return [operator_dict[op] for op in selected_operators]


def get_sub_arn_if_exists(sns_client: BaseClient, topic_arn: str,
                          subscription_type: str, value: str) -> str:
    """Retrieves subscription ARN if subscription is active."""

    response = sns_client.list_subscriptions_by_topic(TopicArn=topic_arn)
    subscriptions = response.get('Subscriptions', [])

    for subscription in subscriptions:
        if subscription['Protocol'] == subscription_type and \
           subscription['Endpoint'] == value and \
           subscription['SubscriptionArn'] != 'Deleted' and \
           subscription['SubscriptionArn'] != 'PendingConfirmation':
            return subscription['SubscriptionArn']

    return None


def subscribe_to_topic(sns_client: BaseClient, topic_arn: str, sub_type: str,
                       value: str, selected_operators: list) -> str:
    """Subscribes an email address or mobile to an Amazon SNS topic."""

    if not get_sub_arn_if_exists(sns_client, topic_arn, sub_type, value):

        response = sns_client.subscribe(
            TopicArn=topic_arn,
            Protocol=sub_type,
            Endpoint=value,
            ReturnSubscriptionArn=True,
            Attributes={
                'FilterPolicy': json.dumps({'operators': selected_operators})
            }
        )
        return response

    return None


def subscribe_or_update(sns_client: BaseClient, topic_arn: str, sub_type: str,
                        value: str, selected_operators: list) -> bool:
    """Subscribe or update existing subscription with filter policy."""

    existing_sub_arn = get_sub_arn_if_exists(
        sns_client, topic_arn, sub_type, value)

    if not existing_sub_arn:
        subscribe_to_topic(sns_client, topic_arn, sub_type,
                           value, selected_operators)
        st.success(
            f"Please check your {sub_type} notifications to confirm subscription.")
        return True

    existing_operators = ", ".join(
        list(get_existing_filter_policy(sns_client, existing_sub_arn)['operators']))
    st.warning(
        f"""You are already subscribed via {sub_type} to the following operators:
          {existing_operators}. If you have selected any additional operators,
            we will update your preferences.""")
    update_filter_policy(sns_client, selected_operators, existing_sub_arn)
    return False


def get_sub_attributes(sns_client: BaseClient, sub_arn: str) -> dict:
    """Returns subscription attributes."""

    return sns_client.get_subscription_attributes(SubscriptionArn=sub_arn)['Attributes']


def get_existing_filter_policy(sns_client: BaseClient, sub_arn: str) -> dict:
    """Get existing subscription filter policy."""

    attributes = get_sub_attributes(sns_client, sub_arn)
    return json.loads(attributes.get('FilterPolicy', '{}'))


def update_filter_policy(sns_client: BaseClient, selected_operators: list, sub_arn: str) -> None:
    """Update subscription filter policy."""

    existing_filter_policy = get_existing_filter_policy(sns_client, sub_arn)

    for operator in selected_operators:
        if operator not in existing_filter_policy['operators']:
            existing_filter_policy['operators'].append(operator)

    updated_filter_policy = json.dumps(existing_filter_policy)

    sns_client.set_subscription_attributes(
        SubscriptionArn=sub_arn,
        AttributeName='FilterPolicy',
        AttributeValue=updated_filter_policy
    )


def on_submit(sns_client: BaseClient, topic_arn: str, selected_operators: list,
              email: str = None, mobile: str = None) -> None:
    """Checks entered details and subscribes or updates preferences."""

    if email:
        subscribe_or_update(sns_client, topic_arn, 'email',
                            email, selected_operators)
    if mobile:
        subscribe_or_update(sns_client, topic_arn, 'sms',
                            mobile, selected_operators)
