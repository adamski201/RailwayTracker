"""Contains SQL queries for the archiving process."""

# SQL queries for station_performance
DELAYS_PER_DAY = """
SELECT
    stations.crs_code, stations.station_name, COUNT(*) AS number_of_delays, DATE(scheduled_arrival) AS day
FROM
    arrivals
JOIN
    stations ON arrivals.station_id = stations.station_id
WHERE
    arrivals.scheduled_arrival < CURRENT_DATE - INTERVAL '5 days'
        AND
    arrivals.actual_arrival > arrivals.scheduled_arrival
GROUP BY
    stations.station_id, stations.station_name, day
ORDER BY
    day;
"""

DELAYS_PER_DAY_OVER_5_MIN = """
SELECT
    stations.crs_code, stations.station_name, COUNT(*) AS number_of_delays_over_5_min
FROM
    arrivals
JOIN
     stations ON arrivals.station_id = stations.station_id
WHERE
    arrivals.scheduled_arrival < CURRENT_DATE - INTERVAL '7 days'
        AND
    arrivals.actual_arrival > arrivals.scheduled_arrival + INTERVAL '5 minutes'
GROUP BY
    stations.station_id, stations.station_name;
"""

# SQL queries for operator_performance
