"""Main script for data pipeline."""

from datetime import date, timedelta
from os import environ as ENV

import psycopg2
from dotenv import load_dotenv

from performance_extract import fetch_train_services_data_for_station, load_row_from_csv
from performance_load import upload_arrivals, upload_cancellations
from performance_transform import transform_train_services_data

STATIONS_FILENAME = "stations.csv"

DAY_DELTA = 1

if __name__ == "__main__":
    load_dotenv()

    conn = psycopg2.connect(
        database=ENV["DB_NAME"],
        user=ENV["DB_USER"],
        password=ENV["DB_PASS"],
        host=ENV["DB_HOST"],
        port=ENV["DB_PORT"],
    )

    date = date.today() - timedelta(days=DAY_DELTA)

    stations = load_row_from_csv(STATIONS_FILENAME)

    for station in stations:
        services = fetch_train_services_data_for_station(
            station,
            date,
            username=ENV["REALTIME_API_USER"],
            password=ENV["REALTIME_API_PASS"],
        )

        arrivals, cancellations = transform_train_services_data(services, date)

        upload_arrivals(conn=conn, arrivals=arrivals)
        upload_cancellations(conn=conn, cancellations=cancellations)

    conn.close()
