"""Extract script for the station_performance pipeline."""

from os import environ as ENV
from datetime import datetime

import requests
from requests.auth import HTTPBasicAuth


def fetch_train_data_for_station(station_crs) -> list[dict]:
    """This function accepts the crs code of a station and returns a list of dictionaries.
    Each dictionary represents a train that arrived at the station or intended to arrive
    at the station on this current day.
    The keys of the dictionary correspond to information about the train, the service
    of the train, its arrival/departure times, or information on cancellations."""

    now = datetime.now()
    response = requests.get(
        (
            f"https://api.rtt.io/api/v1/json/search/"
            f"{station_crs}/{now.strftime('%Y')}/{now.strftime('%m')}/{now.strftime('%d')}"
        ),
        auth=HTTPBasicAuth(ENV["REALTIME_API_USER"], ENV["REALTIME_API_PASS"]),
    )

    response.raise_for_status()

    return response.json()["services"]
