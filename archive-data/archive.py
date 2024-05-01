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

from archive_queries import (S_DELAYS, S_DELAYS_OVER_5_MIN, S_AVG_DELAY, S_TOTAL_ARRIVALS, S_TOTAL_CANCELLATIONS,
                             O_DELAYS, O_DELAYS_OVER_5_MIN, O_AVG_DELAY, O_TOTAL_ARRIVALS, O_TOTAL_CANCELLATIONS,
                             INSERT_STATION_PERFORMANCE, INSERT_OPERATOR_PERFORMANCE,
                             DELETE_OLD_ARRIVAL_DATA, DELETE_OLD_CANCELLATION_DATA)


class DataFetchError(Exception):
    """Exception raised when there is an error fetching data."""
    pass


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
        raise DataFetchError("No data fetched from the database.")

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
        raise DataFetchError("No data fetched from the database.")

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

    station_queries = [S_DELAYS, S_DELAYS_OVER_5_MIN, S_AVG_DELAY, S_TOTAL_ARRIVALS, S_TOTAL_CANCELLATIONS]
    operator_queries = [O_DELAYS, O_DELAYS_OVER_5_MIN, O_AVG_DELAY, O_TOTAL_ARRIVALS, O_TOTAL_CANCELLATIONS]
    deletion_queries = [DELETE_OLD_ARRIVAL_DATA, DELETE_OLD_CANCELLATION_DATA]

    load_dotenv()
    conn = get_db_connection(ENV)

    stations_data = clean_data(get_stations_performance(conn, station_queries))
    operators_data = clean_data(get_operators_performance(conn, operator_queries))

    load_to_db(conn, convert_to_list(stations_data), INSERT_STATION_PERFORMANCE)
    load_to_db(conn, convert_to_list(operators_data), INSERT_OPERATOR_PERFORMANCE)

    delete_old_data(conn, deletion_queries)

    close_connection(conn)

    return {
        "status": "Success!"
    }


if __name__ == "__main__":
    load_dotenv()

    conn = get_db_connection(ENV)

    station_queries = [S_DELAYS, S_DELAYS_OVER_5_MIN, S_AVG_DELAY, S_TOTAL_ARRIVALS, S_TOTAL_CANCELLATIONS]
    operator_queries = [O_DELAYS, O_DELAYS_OVER_5_MIN, O_AVG_DELAY, O_TOTAL_ARRIVALS, O_TOTAL_CANCELLATIONS]

    stations_data = clean_data(get_stations_performance(conn, station_queries))
    operators_data = clean_data(get_operators_performance(conn, operator_queries))

    load_to_db(conn, convert_to_list(stations_data), INSERT_STATION_PERFORMANCE)
    load_to_db(conn, convert_to_list(operators_data), INSERT_OPERATOR_PERFORMANCE)

    deletion_queries = [DELETE_OLD_ARRIVAL_DATA, DELETE_OLD_CANCELLATION_DATA]
    delete_old_data(conn, deletion_queries)

    close_connection(conn)