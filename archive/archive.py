"""This file is responsible for moving old data from
the short-term storage to the long-term storage."""

from functools import reduce
import logging
from os import environ as ENV

from dotenv import load_dotenv
from psycopg2 import connect, Error
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection
import pandas as pd

from sql_queries import (S_DELAYS, S_DELAYS_OVER_5_MIN, S_AVG_DELAY,
                         S_TOTAL_ARRIVALS, S_TOTAL_CANCELLATIONS,
                         O_DELAYS, O_DELAYS_OVER_5_MIN, O_AVG_DELAY,
                         O_TOTAL_ARRIVALS, O_TOTAL_CANCELLATIONS,
                         INSERT_STATION_PERFORMANCE, INSERT_OPERATOR_PERFORMANCE,
                         DELETE_OLD_ARRIVAL_DATA, DELETE_OLD_CANCELLATION_DATA)

STATION_QUERIES = [S_DELAYS, S_DELAYS_OVER_5_MIN, S_AVG_DELAY, S_TOTAL_ARRIVALS, S_TOTAL_CANCELLATIONS]
OPERATOR_QUERIES = [O_DELAYS, O_DELAYS_OVER_5_MIN, O_AVG_DELAY, O_TOTAL_ARRIVALS, O_TOTAL_CANCELLATIONS]
DELETION_QUERIES = [DELETE_OLD_ARRIVAL_DATA, DELETE_OLD_CANCELLATION_DATA]
REQUIRED_KEYS = ['day', 'delay_1m_count', 'delay_5m_count', 'avg_delay_min', 'arrival_count', 'cancellation_count']


def setup_logging() -> None:
    """Sets up the logging configuration."""

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s:%(levelname)s:%(message)s')


def get_db_connection(config: dict[str, str]) -> connection:
    """Returns a connection to a database."""

    return connect(
        host=config["DB_HOST"],
        user=config["DB_USER"],
        password=config["DB_PASS"],
        dbname=config["DB_NAME"],
        port=config["DB_PORT"],
        cursor_factory=RealDictCursor
    )


def close_connection(conn: connection) -> None:
    """Closes the connection to the database."""

    conn.close()


def fetch_old_data(conn: connection, query: str) -> pd.DataFrame:
    """Fetches historical data based on the query.
    Returns the fetched data as a DataFrame."""

    try:

        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()

        if not rows:
            logging.warning("No data fetched for query: %s", query)

        return pd.DataFrame(rows)

    except Error as err:

        conn.rollback()
        logging.error("Failed to fetch data: %s", err)
        if err.pgcode:
            logging.error("Error code: %s", err.pgcode)


def get_stations_performance(conn: connection, queries: list[str]) -> pd.DataFrame:
    """Fetches the historical data for the stations based on the queries."""

    performance_data = []  # list for adding the dataframes

    for query in queries:
        result = fetch_old_data(conn, query)
        if not result.empty:
            performance_data.append(result)

    if not performance_data:
        return pd.DataFrame()

    # combines the dataframes
    return reduce(lambda left, right: pd.merge(left, right, on=['day', 'station_id'], how='outer'), performance_data)


def get_operators_performance(conn: connection, queries: list[str]) -> pd.DataFrame:
    """Fetches the historical data for the operators based on the queries."""

    performance_data = []  # list for adding the dataframes

    for query in queries:
        result = fetch_old_data(conn, query)
        if not result.empty:
            performance_data.append(result)

    if not performance_data:
        return pd.DataFrame()

    # combines the dataframes
    return reduce(lambda left, right: pd.merge(left, right, on=['day', 'operator_id'], how='outer'), performance_data)


def clean_data(data: pd.DataFrame) -> pd.DataFrame:
    """Cleans the data by converting the columns to the
    correct data types and filling in the missing values."""

    data['day'] = pd.to_datetime(data['day']).dt.date
    data['delay_1m_count'] = data['delay_1m_count'].fillna(0).astype(int)
    data['delay_5m_count'] = data['delay_5m_count'].fillna(0).astype(int)
    data['avg_delay_min'] = data['avg_delay_min'].fillna(0).astype(int)
    data['arrival_count'] = data['arrival_count'].fillna(0).astype(int)
    data['cancellation_count'] = data['cancellation_count'].fillna(0).astype(int)

    return data


def check_keys_exist(df: pd.DataFrame, keys: list[str]) -> bool:
    """Check if all keys exist in the DataFrame."""

    return all(key in df.columns for key in keys)


def convert_to_list(df: str) -> list[tuple]:
    """Converts a DataFrame to a list of tuples."""

    return df.to_records(index=False).tolist()


def load_to_db(conn: connection, data: list[tuple], query: str) -> None:
    """Loads the data to the database using the query provided."""

    try:
        with conn.cursor() as cur:
            cur.executemany(query, data)
        conn.commit()

    except Error as err:
        conn.rollback()
        logging.error("Failed to load data: %s", err)
        if err.pgcode:
            logging.error("Error code: %s", err.pgcode)


def delete_old_data(conn: connection, queries: list[str]):
    """Deletes old data from 'arrivals' and 'cancellations'
    tables in the database that are older than 30 days."""

    try:
        with conn.cursor() as cur:
            cur.execute("BEGIN;")
            for query in queries:
                cur.execute(query)
            conn.commit()

    except Error as err:
        conn.rollback()
        logging.error("Failed to delete old data: %s", err)
        if err.pgcode:
            logging.error("Error code: %s", err.pgcode)


def handler(event: dict = None, context: dict = None) -> dict:
    """
    Adds logic from main into handler to be used in lambda.
    """

    setup_logging()
    logging.info("Starting the process...")

    load_dotenv()

    try:

        conn = get_db_connection(ENV)
        logging.info("Connected to the database successful.")

        stations_data = get_stations_performance(conn, STATION_QUERIES)
        operators_data = get_operators_performance(conn, OPERATOR_QUERIES)

        if check_keys_exist(stations_data, REQUIRED_KEYS) and check_keys_exist(operators_data, REQUIRED_KEYS):
            logging.info("Required keys exist in the data.")

            stations_data = clean_data(stations_data)
            operators_data = clean_data(operators_data)

            load_to_db(conn, convert_to_list(stations_data), INSERT_STATION_PERFORMANCE)
            load_to_db(conn, convert_to_list(operators_data), INSERT_OPERATOR_PERFORMANCE)

            delete_old_data(conn, DELETION_QUERIES)
            logging.info("Old data deleted successfully.")

            close_connection(conn)
            logging.info("Connection to the database closed.")

            return {
                "statusCode": 200,
                "status": "Success!"
            }

        close_connection(conn)
        logging.info("Connection to the database closed.")

        return {
            "statusCode": 400,
            "body": "Missing required keys in the event data."
        }

    except Exception as e:
        logging.error("An error occurred: %s", {str(e)})

        return {
            "body": "An error occurred"
        }


if __name__ == "__main__":
    pass
