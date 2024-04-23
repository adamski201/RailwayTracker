from os import environ as ENV

import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv


if __name__ == "__main__":

    load_dotenv()

    response = requests.get(
        "https://api.rtt.io/api/v1/json/search/PAD/2024/04/23", auth=HTTPBasicAuth(ENV["REALTIME_API_USER"], ENV["REALTIME_API_PASS"]))

    todays_station_data = response.json()

    # print(todays_station_data["location"])

    services_data = todays_station_data["services"]

    counter = 0

    # keys: service_id, cancellation_code, cancelReason, and station_crs
    cancelled_services = []
    # keys: service_id, scheduled_arrival, actual_arrival, scheduled_departure, actual_departure station_crs
    arrived_services = []
    for service in services_data:

        if "cancelReasonCode" in service["locationDetail"].keys():
            cancelled_service = {}
            cancelled_service["service_id"] = service["serviceUid"]
            cancelled_service["cancellation_code"] = service["locationDetail"]["cancelReasonCode"]
            cancelled_service["cancel_reason"] = service["locationDetail"]["cancelReasonLongText"]
            # maybe don't need to search for this
            cancelled_service["station_crs"] = service["locationDetail"]["crs"]

            cancelled_services.append(cancelled_service)

        else:

            arrived_service = {}
            arrived_service["service_id"] = service["serviceUid"]
            arrived_service["scheduled_arrival"] = service["locationDetail"]["gbttBookedArrival"]
            arrived_service["actual_arrival"] = service["locationDetail"]["realtimeArrival"]
            arrived_service["scheduled_departure"] = service["locationDetail"]["gbttBookedDeparture"]
            arrived_service["actual_departure"] = service["locationDetail"]["realtimeArrival"]

    print(cancelled_services)
