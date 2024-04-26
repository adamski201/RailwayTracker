"""An extract script to retrieve live data from the
Knowledgebase (KB) Real Time Incidents API"""

from time import sleep
from os import environ as ENV
import logging

from dotenv import load_dotenv
import stomp

from transform import transform_message
from load import load_to_database


class TrainListener(stomp.ConnectionListener):
    """Provides methods to handle live data stream"""

    def on_error(self, frame):
        """Executes on error"""
        logging.info('Received an error %s', frame.body)

    def on_disconnected(self):
        """Executes if disconnection occurs"""

        logging.warning('Disconnected - attempting to reconnect...')
        sleep(15)
        initialise_connection(ENV)

    def on_message(self, frame):
        """Executes when message is received"""

        logging.info('Received message')
        cleaned_msg = transform_message(frame.body)
        load_to_database(ENV, cleaned_msg)


def get_stomp_conn(config: dict[str, str]):
    """Returns STOMP connection"""

    return stomp.Connection12([(config["HOST"],
                                config["STOMP_PORT"])],
                              reconnect_sleep_initial=1,
                              reconnect_sleep_increase=1,
                              reconnect_attempts_max=30)


def connect_and_subscribe(connection: stomp.StompConnection12, admin: str,
                          passcode: str, sub_topic: str) -> None:
    """Connects and subscribes to relevant topic"""

    connection.connect(admin, passcode, wait=True)
    connection.subscribe(destination=f'/topic/{sub_topic}', id=1, ack='auto')


def initialise_connection(config: dict[str, str]) -> None:
    """Starts/resets connection"""

    conn = get_stomp_conn(config)
    conn.set_listener('', TrainListener())
    connect_and_subscribe(conn, username, password, topic)
    maintain_connection(conn)


def maintain_connection(connection: stomp.Connection12) -> None:
    """Maintains STOMP connection"""

    try:
        logging.info('Listening for KB messages...')
        while True:
            sleep(1)
    except KeyboardInterrupt:
        logging.info('Exiting...')
        connection.disconnect()


if __name__ == "__main__":

    load_dotenv()

    logging.basicConfig(level=logging.INFO)

    username = ENV["USERNAME"]
    password = ENV["PASSWORD"]
    topic = ENV["INCIDENTS_TOPIC"]

    initialise_connection(ENV)
