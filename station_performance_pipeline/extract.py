"""Extract script for the station_performance pipeline."""

from datetime import date
import csv
import requests
from requests.auth import HTTPBasicAuth

RTT_API_URL = "https://api.rtt.io/api/v1/json/search/"


def fetch_train_services_data_for_station(
    station_crs, date: date, username: str, password: str
) -> list[dict]:
    """This function accepts the crs code of a station and returns a list of dictionaries.
    Each dictionary represents a train that arrived at the station or intended to arrive
    at the station on this current day.
    The keys of the dictionary correspond to information about the train, the service
    of the train, its arrival/departure times, or information on cancellations."""

    response = requests.get(
        f"{RTT_API_URL}{station_crs}/{date.year}/{date.month:02d}/{date.day:02d}",
        auth=HTTPBasicAuth(username, password),
        timeout=60,
    )

    response.raise_for_status()

    if "services" not in response.json().keys():
        raise ValueError(f"Station {station_crs} caused an error: {response.text}")

    return response.json()["services"]


def load_row_from_csv(
    filename: str, row_index: int = 0, has_header: bool = False
) -> list[str]:
    """
    Load data from a single row of a CSV file.
    If a header is present, row zero is the first non-header row.
    """
    with open(filename, mode="r", encoding="UTF-8") as file:
        reader = csv.reader(file)
        if has_header:
            next(reader)
        return list(reader)[row_index]
