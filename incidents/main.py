"""A pipeline script to retrieve live data from the Knowledgebase
(KB) Real Time Incidents API, transform it, send alerts to
subscribers via email and/or sms and load data into the database."""

from os import environ as ENV
from dotenv import load_dotenv
import logging

from boto3 import client

from extract import initialise_connection


if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s:%(levelname)s:%(message)s')

    load_dotenv()

    topic_arn = ENV["TOPIC_ARN"]

    sns = client('sns', region_name='eu-west-2')

    initialise_connection(ENV, sns)
