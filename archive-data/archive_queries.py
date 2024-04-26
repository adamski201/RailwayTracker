"""Contains SQL queries for the archiving process."""

# Station_performance queries
S_DELAYS = """
SELECT
    arrivals.station_id, DATE(scheduled_arrival) AS day, COUNT(*) AS delay_1m_count
FROM
    arrivals
WHERE
    arrivals.scheduled_arrival < CURRENT_DATE - INTERVAL '7 days'
        AND
    arrivals.actual_arrival > arrivals.scheduled_arrival
GROUP BY
    arrivals.station_id , day
ORDER BY
    day, arrivals.station_id ASC;
"""

S_DELAYS_OVER_5_MIN = """
SELECT
    arrivals.station_id, DATE(scheduled_arrival) AS day, COUNT(*) AS delay_5m_count
FROM
    arrivals
WHERE
    arrivals.scheduled_arrival < CURRENT_DATE - INTERVAL '7 days'
        AND
    arrivals.actual_arrival > arrivals.scheduled_arrival + INTERVAL '5 minutes'
GROUP BY
    arrivals.station_id, day
ORDER BY
    day, arrivals.station_id ASC;
"""

S_AVG_DELAY = """
SELECT
    arrivals.station_id, DATE(scheduled_arrival) AS day,
    ROUND(AVG(EXTRACT(EPOCH FROM (arrivals.actual_arrival - arrivals.scheduled_arrival))/60), 2) AS avg_delay_min
FROM
    arrivals
WHERE
    arrivals.scheduled_arrival < CURRENT_DATE - INTERVAL '7 days'
        AND
    arrivals.actual_arrival > arrivals.scheduled_arrival
GROUP BY
    arrivals.station_id, day
ORDER BY
    day, arrivals.station_id ASC;
"""

S_TOTAL_ARRIVALS = """
SELECT
    arrivals.station_id, DATE(scheduled_arrival) AS day, COUNT(*) AS arrival_count
FROM
    arrivals
WHERE
    arrivals.scheduled_arrival < CURRENT_DATE - INTERVAL '7 days'
GROUP BY
    arrivals.station_id, day
ORDER BY
    day, arrivals.station_id ASC;
"""

S_TOTAL_CANCELLATIONS = """
SELECT
    cancellations.station_id, DATE(cancellations.scheduled_arrival) AS day, COUNT(*) AS cancellation_count
FROM
    cancellations
WHERE
    cancellations.scheduled_arrival < CURRENT_DATE - INTERVAL '1 days'
GROUP BY
    cancellations.station_id, day
ORDER BY
    day, arrivals.station_id ASC;
"""

S_COMMON_CANCELLATION = """
WITH
    cancellation_counts
        AS (
          SELECT
                stations.station_id, stations.station_name, DATE(cancellations.scheduled_arrival) AS day,
                cancellations.cancellation_type_id, COUNT(*) AS count
          FROM
                cancellations
          JOIN
                stations ON cancellations.station_id = stations.station_id
          WHERE
              cancellations.scheduled_arrival < CURRENT_DATE - INTERVAL '6 days'
          GROUP BY
              stations.station_id,stations.station_name, DATE(cancellations.scheduled_arrival), cancellations.cancellation_type_id
            ),
    ranked_cancellation_types
        AS (
            SELECT
                station_id, station_name, day,
                cancellation_type_id, count,
                RANK() OVER (PARTITION BY station_id, day ORDER BY count DESC) AS rank
            FROM
                cancellation_counts
            )
SELECT
    station_id, station_name, day,
    cancellation_type_id AS common_cancel_code
FROM
    ranked_cancellation_types
WHERE
rank = 1;
"""

# Operator_performance queries
