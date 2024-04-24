from os import environ as ENV
from datetime import datetime

import requests
from requests.auth import HTTPBasicAuth


def get_station_train_services_data(station_crs) -> list[dict]:
    """This function accepts the crs code of a station and returns a list of dictionaries.
    Each dictionary represents a train that arrived at the station or intended to arrive
    at the station on this current day.
    The keys of the dictionary correspond to information about the train, the service
    of the train, its arrival/departure times, or information on cancellations."""

    now = datetime.now()
    response = requests.get(
        f"https://api.rtt.io/api/v1/json/search/{station_crs}/{now.strftime('%Y')}/{now.strftime('%m')}/{now.strftime('%d')}", auth=HTTPBasicAuth(ENV["REALTIME_API_USER"], ENV["REALTIME_API_PASS"]))

    if response.status_code != 200:
        raise requests.RequestException(
            f"Failed to fetch data: {response.text}")

    else:
        todays_station_data = response.json()
        return todays_station_data["services"]


def train_station_arrival_data(train_services: list[dict]) -> list[dict]:
    """This function accepts a list of dictionaries corresponding to the trains that arrived, 
    or were expected to arrive, at a specific station and returns another list of dictionaries.
    Each dictionary represents a train that arrived at the station on this day, extracting only relevant data
    from the inputted list.
    The dictionary has the keys related to the expected and actual times of arrival and departure."""

    if len(train_services) != 0:
        station_crs = train_services[0]["locationDetail"]["crs"]
        station_name = train_services[0]["locationDetail"]["description"]

        arrived_services = []
        for service in train_services:

            if "cancelReasonCode" not in service["locationDetail"].keys():

                arrived_service = {}
                arrived_service["service_id"] = service["serviceUid"]
                if "gbttBookedArrival" in service["locationDetail"].keys():
                    arrived_service["scheduled_arrival"] = service["locationDetail"]["gbttBookedArrival"]
                    arrived_service["actual_arrival"] = service["locationDetail"]["realtimeArrival"]
                if "gbttBookedDeparture" in service["locationDetail"].keys():
                    arrived_service["scheduled_departure"] = service["locationDetail"]["gbttBookedDeparture"]
                    arrived_service["actual_departure"] = service["locationDetail"]["realtimeDeparture"]
                arrived_service["station_crs"] = station_crs
                arrived_service["station_name"] = station_name
                arrived_service["atocCode"] = service["atocCode"]
                arrived_service["atocName"] = service["atocName"]

                arrived_services.append(arrived_service)

        return arrived_services

    else:
        return []


def train_station_cancellation_data(train_services: list[dict]) -> list[dict]:
    """This function accepts a list of dictionaries corresponding to the trains that arrived, 
    or were expected to arrive, at a specific station and returns another list of dictionaries.
    Each dictionary represents a train that had intended to arrive that day, but was cancelled.
    The outputted dictionaries contain a (relevant) subset of the inputted data related
    to the reasons of cancellation."""

    if len(train_services) != 0:
        station_crs = train_services[0]["locationDetail"]["crs"]
        station_name = train_services[0]["locationDetail"]["description"]

        cancelled_services = []
        for service in train_services:

            if "cancelReasonCode" in service["locationDetail"].keys():
                cancelled_service = {}
                cancelled_service["service_id"] = service["serviceUid"]
                cancelled_service["cancellation_code"] = service["locationDetail"]["cancelReasonCode"]
                cancelled_service["cancel_reason"] = service["locationDetail"]["cancelReasonLongText"]
                cancelled_service["station_crs"] = station_crs
                cancelled_service["station_name"] = station_name
                cancelled_service["atocCode"] = service["atocCode"]
                cancelled_service["atocName"] = service["atocName"]

                cancelled_services.append(cancelled_service)

        return cancelled_services

    else:
        return []
