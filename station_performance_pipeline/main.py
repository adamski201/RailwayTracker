"""Main script for data pipeline."""

from dotenv import load_dotenv

from extract import (
    extract_train_data_for_station,
)

if __name__ == "__main__":

    load_dotenv()

    paddington_train_services = extract_rtt_data_for_station("PAD")

    print(paddington_train_services)

    paddington_arrivals = train_station_arrival_data(paddington_train_services)

    paddington_cancellations = train_station_cancellation_data(
        paddington_train_services
    )
