import pandas as pd
from psycopg2._psycopg import cursor
from dotenv import load_dotenv


load_dotenv()


def get_station_names(cur: cursor) -> list[str]:
    """Retrieves station names from the database."""
    cur.execute(
        """
        SELECT station_name
        FROM stations
        ORDER BY station_name ASC
        """
    )

    return [x[0] for x in cur.fetchall()]


def get_total_arrivals_for_station(
    cur: cursor, station_name: str, days_delta: int
) -> int:
    """
    Gets the total number of arrivals for a given station since the
    provided number of days in the past.
    """
    cur.execute(
        """
        SELECT COUNT(*)
        FROM arrivals
        LEFT JOIN stations
            ON arrivals.station_id = stations.station_id
        WHERE stations.station_name LIKE %s
        AND scheduled_arrival >= DATE_TRUNC('day', NOW() - INTERVAL '%s day')
        """,
        (station_name, days_delta),
    )

    return cur.fetchone()[0]


def get_total_cancellations_for_station(
    cur: cursor, station_name: str, days_delta: int
) -> int:
    """
    Gets the total number of cancellations for a given station since the
    provided number of days in the past.
    """
    cur.execute(
        """
        SELECT COUNT(*)
        FROM cancellations
        LEFT JOIN stations
            ON cancellations.station_id = stations.station_id
        WHERE stations.station_name LIKE %s
        AND scheduled_arrival >= DATE_TRUNC('day', NOW() - INTERVAL '%s day')
        """,
        (station_name, days_delta),
    )

    return cur.fetchone()[0]


def get_total_delays_for_station(
    cur: cursor, threshold: int, station_name: str, days_delta: int
) -> int:
    """
    Gets the total number of cancellations for a given station since the
    provided number of days in the past.
    """
    cur.execute(
        """
        SELECT COUNT(*)
        FROM arrivals
        LEFT JOIN stations
            ON arrivals.station_id = stations.station_id
        WHERE stations.station_name LIKE %s
        AND EXTRACT(EPOCH FROM actual_arrival - scheduled_arrival)/60 > %s
        AND scheduled_arrival >= DATE_TRUNC('day', NOW() - INTERVAL '%s day')
        """,
        (station_name, threshold, days_delta),
    )

    return cur.fetchone()[0]


def get_arrivals_for_station(
    cur: cursor, station_name: str, days_delta: int
) -> pd.DataFrame:
    """
    Gets selected information about individual arrivals at a station since the
    provided number of days in the past.
    """
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
        WHERE station_name = %s
        AND scheduled_arrival >= DATE_TRUNC('day', NOW() - INTERVAL '%s day')
        """,
        (station_name, days_delta),
    )

    return pd.DataFrame(cur.fetchall())


def get_delay_breakdown_for_station(
    cur: cursor, station_name: str, delay_threshold: int, days_delta: int = 30
) -> pd.DataFrame:
    """
    Gets a breakdown of delays grouped by half-hour of the day averaged over the number
    of days specified in days_delta. The threshold for what is considered a delay is
    provided by delay_threshold.
    """
    query = """
    WITH total_arrivals AS (
    SELECT COUNT(*) as count
    FROM arrivals
    LEFT JOIN stations
    ON arrivals.station_id = stations.station_id
    WHERE station_name = %s
    AND scheduled_arrival >= DATE_TRUNC('day', NOW() - INTERVAL '%s day'))
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

    params = (station_name, days_delta, delay_threshold, station_name, days_delta)

    cur.execute(query, params)

    return pd.DataFrame(cur.fetchall(), columns=["interval_start", "pct_delayed"])


def get_daily_stats(
    cur: cursor, station_name: str, delay_threshold: int, days_delta: int = 30
) -> pd.DataFrame:
    """
    Gets a summary of daily stats for a given station, including total arrivals,
    cancellations, and delays, returning this information as a dataframe.
    """
    query = """
    WITH total_cancellations AS (
        SELECT
            COUNT(*) AS cancellations,
            DATE_TRUNC('day', scheduled_arrival) AS date
        FROM cancellations
        LEFT JOIN stations
            ON cancellations.station_id = stations.station_id
        WHERE station_name = %s
        AND scheduled_arrival >= DATE_TRUNC('day', NOW() - INTERVAL '%s day')
        GROUP BY date
    ) SELECT total_delays.date AS date, arrivals, delays, cancellations
    FROM (
    SELECT
        DATE_TRUNC('day', scheduled_arrival) AS date,
        COUNT(*) AS arrivals,
        SUM(CASE WHEN EXTRACT(EPOCH FROM actual_arrival - scheduled_arrival)/60 >= %s THEN 1 ELSE 0 END) AS delays
    FROM arrivals
    LEFT JOIN stations
        ON arrivals.station_id = stations.station_id
    WHERE station_name = %s
    AND scheduled_arrival >= DATE_TRUNC('day', NOW() - INTERVAL '%s day')
    GROUP BY date) AS total_delays
    INNER JOIN total_cancellations
    ON total_cancellations.date = total_delays.date;
"""

    params = (station_name, days_delta, delay_threshold, station_name, days_delta)

    cur.execute(query, params)

    return pd.DataFrame(
        cur.fetchall(), columns=["date", "arrivals", "delays", "cancellations"]
    )


def get_current_incidents(cur: cursor, station_name: str):
    """
    Returns a dataframe listing all incidents for operators who operate trains
    at the given station.
    """
    query = """
    SELECT DISTINCT(incidents.*)
    FROM incidents
    LEFT JOIN operators
    ON incidents.operator_id = operators.operator_id
    LEFT JOIN services
    ON operators.operator_id = services.operator_id
    lEFT JOIN arrivals
    ON services.service_id = arrivals.service_id
    LEFT JOIN stations
    ON arrivals.station_id = stations.station_id
    WHERE station_name = %s
    ORDER BY creation_date DESC;
    """

    params = (station_name,)

    cur.execute(query, params)

    return pd.DataFrame(
        cur.fetchall(),
        columns=[
            "incident_id",
            "operator_id",
            "incident_uuid",
            "creation_date",
            "last_updated",
            "Start Date",
            "End Date",
            "Planned?",
            "Cleared?",
            "Affected Routes",
            "Summary",
            "info_link",
        ],
    )
