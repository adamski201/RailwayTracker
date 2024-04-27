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


def get_delay_breakdown_for_station(
    station_name: str, delay_threshold: int, days_delta: int = 30
):
    query = """
    WITH total_arrivals AS (
    SELECT COUNT(*) as count
    FROM arrivals
    LEFT JOIN stations
    ON arrivals.station_id = stations.station_id
    WHERE station_name = 'Hemel Hempstead')
SELECT
    CAST(date_trunc('hour', CAST(scheduled_arrival AS TIME)) + (floor(date_part('minute', CAST(scheduled_arrival AS TIME)) / 30) * interval '30 minute') AS TIME)  AS interval_start,
    ROUND((SUM(CASE WHEN EXTRACT(EPOCH FROM actual_arrival - scheduled_arrival)/60 >= %s THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 1) AS delay_percentage
FROM arrivals
LEFT JOIN stations
    ON arrivals.station_id = stations.station_id
LEFT JOIN services
    ON arrivals.service_id = services.service_id
LEFT JOIN operators
    ON services.service_id = operators.operator_id
WHERE station_name = %s
AND scheduled_arrival >= DATE_TRUNC('day', NOW() - INTERVAL '%s day')
GROUP BY interval_start
HAVING count(*) > 0.01 * (SELECT count FROM total_arrivals)
ORDER BY interval_start ASC;
    """

    params = (delay_threshold, station_name, days_delta)

    cur.execute(query, params)

    return pd.DataFrame(cur.fetchall(), columns=["interval_start", "pct_delayed"])
