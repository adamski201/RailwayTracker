"""An extract script to retrieve live data from the
Knowledgebase (KB) Real Time Incidents API"""

from time import sleep
from os import environ as ENV
import logging
from dotenv import load_dotenv
import stomp



def connect_and_subscribe(connection, admin:str, passcode:str, sub_topic:str):
    """Connects and subscribes to relevant topic"""

    connection.connect(admin, passcode, wait=True)
    connection.subscribe(destination=f'/topic/{sub_topic}', id=1, ack='auto')


class TrainListener(stomp.ConnectionListener):
    """Provides methods to handle live data stream"""

    def __init__(self):
        self.reconnect_attempts = 0

    def on_error(self, frame):
        """Executes on error"""
        logging.info(f'Received an error {frame.body}')

    def on_disconnected(self):
        """Executes if disconnection occurs"""

        logging.info('Disconnected - attempting to reconnect...')

        if self.reconnect_attempts >= 20:
            logging.info('Maximum reconnect attempts reached. Exiting...')
        else:
            self.reconnect_attempts += 1
            logging.info(f'Reconnect attempt {self.reconnect_attempts}')
            sleep(10)
            connect_and_subscribe(conn, username, password, topic)


    def on_message(self, frame):
        """Executes when message is received"""
        logging.info(f'Received a message {frame.body}')



def get_stomp_conn(config):
    """Returns STOMP connection"""
    return stomp.Connection12([(config["HOST"],
                                config["STOMP_PORT"])],
                                heartbeats=(4000, 4000),
                                reconnect_sleep_initial=1,
                                reconnect_sleep_increase=2,
                                reconnect_attempts_max=20,
                                heart_beat_receive_scale=2.5)

if __name__ == "__main__":

    load_dotenv()

    logging.basicConfig(level=logging.INFO)

    username = ENV["USERNAME"]
    password = ENV["PASSWORD"]
    topic = ENV["INCIDENTS_TOPIC"]

    conn = get_stomp_conn(ENV)
    conn.set_listener('', TrainListener())
    connect_and_subscribe(conn, username, password, topic)

    try:
        logging.info('Listening for KB messages...')
        while True:
            sleep(1)
    except KeyboardInterrupt:
        logging.info('Exiting...')
        conn.disconnect()
