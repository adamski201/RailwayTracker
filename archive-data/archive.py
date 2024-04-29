"""This file is responsible for moving the historical data from
the short-term storage to the long-term storage"""

from functools import reduce
import logging
from os import environ as ENV

from dotenv import load_dotenv
from psycopg2 import connect, Error
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection
import pandas as pd

from archive_queries import S_DELAYS, S_DELAYS_OVER_5_MIN, S_AVG_DELAY, S_TOTAL_ARRIVALS, S_TOTAL_CANCELLATIONS, \
    O_DELAYS, O_DELAYS_OVER_5_MIN, O_AVG_DELAY, O_TOTAL_ARRIVALS, O_TOTAL_CANCELLATIONS, INSERT_STATION_PERFORMANCE, \
    INSERT_OPERATOR_PERFORMANCE


def setup_logging() -> None:
    """Sets up logging to the terminal"""

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s:%(levelname)s:%(message)s')


def get_db_connection(config: dict[str, str]) -> connection:
    """Returns a connection to a database"""

    return connect(
        host=config["DB_HOST"],
        user=config["DB_USER"],
        password=config["DB_PASS"],
        dbname=config["DB_NAME"],
        port=config["DB_PORT"],
        cursor_factory=RealDictCursor
    )


def close_connection(conn: connection) -> None:
    """Closes the connection to the database"""

    conn.close()


def fetch_and_delete_data(conn: connection, fetch_query: str, delete_query: str) -> pd.DataFrame:
    """Fetches historical data based on the fetch_query
    and then deletes the fetched data using the delete_query.
    Returns the fetched data as a DataFrame"""

    try:
        with conn.cursor() as cur:
            cur.execute("BEGIN;")

            cur.execute(fetch_query)
            rows = cur.fetchall()

            cur.execute(delete_query)

            conn.commit()
        return pd.DataFrame(rows)

    except psycopg2.Error as err:
        conn.rollback()
        logging.error("An error occurred: %s", err)
        if err.pgcode:
            logging.error("Error code: %s", err.pgcode)
        if err.pgerror:
            logging.error("Detailed error: %s", err.pgerror)


def get_stations_performance(conn: connection, queries: list[str]) -> pd.DataFrame:
    """Fetches the historical data for the stations based on the queries"""

    performance_data = []  # list for adding the dataframes

    for query in queries:
        result = fetch_and_delete_data(conn, query)
        print("done")
        if result is not None:
            performance_data.append(result)

    # combines the dataframes
    return reduce(lambda left, right: pd.merge(left, right, on=['day', 'station_id'], how='outer'), performance_data)


def get_operators_performance(conn: connection, queries: list[str]) -> pd.DataFrame:
    """Fetches the historical data for the operators based on the queries"""

    performance_data = []  # list for adding the dataframes

    for query in queries:
        result = fetch_and_delete_data(conn, query)
        print("done")
        if result is not None:
            performance_data.append(result)

    # combines the dataframes
    return reduce(lambda left, right: pd.merge(left, right, on=['day', 'operator_id'], how='outer'), performance_data)


def clean_data(data: pd.DataFrame) -> pd.DataFrame:
    """Cleans the data by converting the columns to the
    correct data types and filling in the missing values"""

    data['day'] = pd.to_datetime(data['day']).dt.date
    data['delay_1m_count'] = data['delay_1m_count'].fillna(0).astype(int)
    data['delay_5m_count'] = data['delay_5m_count'].fillna(0).astype(int)
    data['avg_delay_min'] = data['avg_delay_min'].fillna(0).astype(int)
    data['cancellation_count'] = data['cancellation_count'].fillna(0).astype(int)

    return data


def convert_to_list(df: str) -> list[tuple]:
    """Converts a DataFrame to a list of tuples"""

    return df.to_records(index=False).tolist()


def load_to_db(conn: connection, data: list[tuple], query: str) -> None:
    """Adds the data to the database"""

    try:
        with conn.cursor() as cur:
            cur.executemany(query, data)
        conn.commit()

    except psycopg2.Error as err:
        conn.rollback()
        logging.error("An error occurred: %s", err)
        if err.pgcode:
            logging.error("Error code: %s", err.pgcode)
        if err.pgerror:
            logging.error("Detailed error: %s", err.pgerror)


def save_to_csv(data: pd.DataFrame, filename: str) -> None:
    """Saves the data to a csv file
    FOR DEBUGGING PURPOSES ONLY!
    """

    data.to_csv(filename, index=False)


if __name__ == "__main__":
    load_dotenv()

    conn = get_db_connection(ENV)

    station_queries = [S_DELAYS, S_DELAYS_OVER_5_MIN, S_AVG_DELAY, S_TOTAL_ARRIVALS, S_TOTAL_CANCELLATIONS]
    operator_queries = [O_DELAYS, O_DELAYS_OVER_5_MIN, O_AVG_DELAY, O_TOTAL_ARRIVALS, O_TOTAL_CANCELLATIONS]

    stations_data = clean_data(get_stations_performance(conn, station_queries))
    operators_data = clean_data(get_operators_performance(conn, operator_queries))

    # save_to_csv(stations_data, 'stations_data.csv')
    # save_to_csv(operators_data, 'operators_data.csv')

    load_to_db(conn, convert_to_list(stations_data), INSERT_STATION_PERFORMANCE)
    load_to_db(conn, convert_to_list(stations_data), INSERT_OPERATOR_PERFORMANCE)

    close_connection(conn)
