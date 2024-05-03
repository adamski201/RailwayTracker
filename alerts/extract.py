"""Functions to receive live data from the
Knowledgebase (KB) Real Time Incidents API
and process each message upon receipt."""

from time import sleep
from os import environ as ENV
import logging

from botocore.client import BaseClient
import stomp

from transform import transform_data
from load import load_data_to_database
from publish import send_alerts

NS = {"ns": "http://nationalrail.co.uk/xml/incident",
      "com": "http://nationalrail.co.uk/xml/common"}


class TrainListener(stomp.ConnectionListener):
    """Provides methods to handle live data stream."""

    def __init__(self, sns_client: BaseClient, config: dict[str, str]):
        self.sns_client = sns_client
        self.config = config

    def on_error(self, frame):
        """Executes on error."""
        logging.info('Received an error %s', frame.body)

    def on_disconnected(self):
        """Executes if disconnection occurs."""

        logging.warning('Disconnected - attempting to reconnect...')
        sleep(15)
        initialise_connection(ENV, self.sns_client)

    def on_message(self, frame):
        """Executes when message is received."""

        logging.info('Received message')
        message = transform_data(frame.body, NS)

        if message:
            logging.info('Data has been cleaned, incident ID = %s',
                         message["incident_number"])
            send_alerts(self.sns_client, message, self.config["TOPIC_ARN"])
            logging.info('Message sent to subscribers')
            load_data_to_database(ENV, message)
            logging.info('Data has been inserted into database')

    def on_heartbeat(self):
        """Executes when heartbeat is received from server."""

        logging.info("Heartbeat received")


def get_stomp_conn(config: dict[str, str]):
    """Returns STOMP connection."""

    return stomp.Connection12([(config["HOST"],
                                config["STOMP_PORT"])],
                              heartbeats=(30000, 30000),
                              reconnect_sleep_initial=1,
                              reconnect_sleep_increase=1,
                              reconnect_attempts_max=30)


def connect_and_subscribe(connection: stomp.StompConnection12, admin: str,
                          passcode: str, sub_topic: str) -> None:
    """Connects and subscribes to relevant topic."""

    connection.connect(admin, passcode, wait=True)
    connection.subscribe(destination=f'/topic/{sub_topic}', id=1, ack='auto')


def maintain_connection(connection: stomp.Connection12) -> None:
    """Maintains STOMP connection."""

    try:
        logging.info('Listening for KB messages...')
        while True:
            sleep(1)
    except KeyboardInterrupt:
        logging.info('Exiting...')
        connection.disconnect()


def initialise_connection(config: dict[str, str], sns_client: BaseClient) -> None:
    """Starts/resets connection."""

    conn = get_stomp_conn(config)
    conn.set_listener('', TrainListener(sns_client, config))
    connect_and_subscribe(conn, config["USERNAME"],
                          config["PASSWORD"], config["INCIDENTS_TOPIC"])
    maintain_connection(conn)
