from os import environ as ENV
from datetime import datetime

import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv


def train_station_arrival_data(station_crs: str) -> list[dict]:
    '''This function accepts the crs code of a station and returns a list of dictionaries.
    Each dictionary represents a train that arrived at the station on this day.
    The dictionary has the keys related to the expected and actual times of arrival and departure.'''

    now = datetime.now()
    response = requests.get(
        F"https://api.rtt.io/api/v1/json/search/{station_crs}/{now.strftime('%Y')}/{now.strftime('%m')}/{now.strftime('%d')}", auth=HTTPBasicAuth(ENV["REALTIME_API_USER"], ENV["REALTIME_API_PASS"]))

    todays_station_data = response.json()

    # Data on all of the instances of services running stopping at teh station
    services_data = todays_station_data["services"]

    arrived_services = []
    for service in services_data:

        if "cancelReasonCode" not in service["locationDetail"].keys():

            arrived_service = {}
            arrived_service["service_id"] = service["serviceUid"]
            if "gbttBookedArrival" in service["locationDetail"].keys():
                arrived_service["scheduled_arrival"] = service["locationDetail"]["gbttBookedArrival"]
                arrived_service["actual_arrival"] = service["locationDetail"]["realtimeArrival"]
            if "gbttBookedDeparture" in service["locationDetail"].keys():
                arrived_service["scheduled_departure"] = service["locationDetail"]["gbttBookedDeparture"]
                arrived_service["actual_departure"] = service["locationDetail"]["realtimeDeparture"]
            # maybe don't need to search for this every time
            arrived_service["station_crs"] = service["locationDetail"]["crs"]
            arrived_service["station_name"] = service["locationDetail"]["description"]
            arrived_service["atocCode"] = service["atocCode"]
            arrived_service["atocName"] = service["atocName"]

            arrived_services.append(arrived_service)

    return arrived_services


def train_station_cancellation_data(station_crs: str) -> list[dict]:
    '''This function accepts the crs code of a station and returns a list of dictionaries.
    Each dictionary represents a train that  had intended to arrive that day, but was cancelled. 
    The dictionary has the keys related to the reasons of cancellation.'''

    now = datetime.now()
    response = requests.get(
        F"https://api.rtt.io/api/v1/json/search/{station_crs}/{now.strftime('%Y')}/{now.strftime('%m')}/{now.strftime('%d')}", auth=HTTPBasicAuth(ENV["REALTIME_API_USER"], ENV["REALTIME_API_PASS"]))

    todays_station_data = response.json()

    # Data on all of the instances of services running stopping at teh station
    services_data = todays_station_data["services"]

    cancelled_services = []
    for service in services_data:

        if "cancelReasonCode" in service["locationDetail"].keys():
            cancelled_service = {}
            cancelled_service["service_id"] = service["serviceUid"]
            cancelled_service["cancellation_code"] = service["locationDetail"]["cancelReasonCode"]
            cancelled_service["cancel_reason"] = service["locationDetail"]["cancelReasonLongText"]
            # maybe don't need to search for this every time
            cancelled_service["station_crs"] = service["locationDetail"]["crs"]
            cancelled_service["station_name"] = service["locationDetail"]["description"]
            cancelled_service["atocCode"] = service["atocCode"]
            cancelled_service["atocName"] = service["atocName"]

            cancelled_services.append(cancelled_service)

    return cancelled_services


if __name__ == "__main__":

    load_dotenv()

    arrivals_list = train_station_arrival_data("PAD")

    cancellations_list = train_station_cancellation_data("PAD")

    print(len(arrivals_list))
    print(len(cancellations_list))
