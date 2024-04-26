import pandas as pd
import psycopg2
from psycopg2._psycopg import connection, cursor
from dotenv import load_dotenv
from os import environ as ENV
import psycopg2.extras

load_dotenv()

conn = psycopg2.connect(
    database=ENV["DB_NAME"],
    user=ENV["DB_USER"],
    password=ENV["DB_PASS"],
    host=ENV["DB_HOST"],
    port=ENV["DB_PORT"],
)


cur = conn.cursor()


def get_station_names() -> list[str]:
    cur.execute(
        """
        SELECT station_name
        FROM stations
        ORDER BY station_name ASC
        """
    )

    return [x[0] for x in cur.fetchall()]


def get_total_arrivals_for_station(station_name: str) -> int:
    cur.execute(
        """
        SELECT COUNT(*)
        FROM arrivals
        LEFT JOIN stations
            ON arrivals.station_id = stations.station_id
        WHERE stations.station_name LIKE %s
        """,
        (station_name,),
    )

    return cur.fetchone()[0]


def get_total_cancellations_for_station(station_name: str) -> int:
    cur.execute(
        """
        SELECT COUNT(*)
        FROM cancellations
        LEFT JOIN stations
            ON cancellations.station_id = stations.station_id
        WHERE stations.station_name LIKE %s
        """,
        (station_name,),
    )

    return cur.fetchone()[0]


def get_total_delays_for_station(threshold: int, station_name: str) -> int:
    cur.execute(
        """
        SELECT COUNT(*)
        FROM arrivals
        LEFT JOIN stations
            ON arrivals.station_id = stations.station_id
        WHERE stations.station_name LIKE %s
        AND EXTRACT(EPOCH FROM actual_arrival - scheduled_arrival)/60 > %s
        """,
        (station_name, threshold),
    )

    return cur.fetchone()[0]


def get_arrivals_for_station(station_name: str) -> pd.DataFrame:
    cur.execute(
        """
        SELECT services.service_uid, scheduled_arrival, actual_arrival, operator_name, operator_code, station_name, crs_code
        FROM arrivals
        LEFT JOIN stations
            ON arrivals.station_id = stations.station_id
        LEFT JOIN services
            ON arrivals.service_id = services.service_id
        LEFT JOIN operators
            ON services.service_id = operators.operator_id
        WHERE station_name = %s""",
        (station_name,),
    )

    return pd.DataFrame(cur.fetchall())
