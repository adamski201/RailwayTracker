from entities import Arrival


def train_station_arrival_data(train_services: list[dict]) -> list[dict]:
    """This function accepts a list of dictionaries corresponding to the trains that
    arrived, or were expected to arrive, at a specific station and returns another
    list of dictionaries.
    Each dictionary represents a train that arrived at the station on this day,
    extracting only relevant data from the inputted list.
    The dictionary has the keys related to the expected and actual times of arrival
    and departure."""

    if len(train_services) != 0:
        station_crs = train_services[0]["locationDetail"]["crs"]
        station_name = train_services[0]["locationDetail"]["description"]

        arrived_services = []
        for service in train_services:

            if "cancelReasonCode" in service["locationDetail"].keys():
                continue

            arrived_service = {"service_id": service["serviceUid"]}
            if "gbttBookedArrival" in service["locationDetail"].keys():
                arrived_service["scheduled_arrival"] = service["locationDetail"][
                    "gbttBookedArrival"
                ]
                arrived_service["actual_arrival"] = service["locationDetail"][
                    "realtimeArrival"
                ]
            if "gbttBookedDeparture" in service["locationDetail"].keys():
                arrived_service["scheduled_departure"] = service["locationDetail"][
                    "gbttBookedDeparture"
                ]
                arrived_service["actual_departure"] = service["locationDetail"][
                    "realtimeDeparture"
                ]
            arrived_service["station_crs"] = station_crs
            arrived_service["station_name"] = station_name
            arrived_service["atoc_code"] = service["atocCode"]
            arrived_service["atoc_name"] = service["atocName"]

            arrived_services.append(arrived_service)

        return arrived_services

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
                cancelled_service = {
                    "service_id": service["serviceUid"],
                    "cancellation_code": service["locationDetail"]["cancelReasonCode"],
                    "cancel_reason": service["locationDetail"]["cancelReasonLongText"],
                    "station_crs": station_crs,
                    "station_name": station_name,
                    "atoc_code": service["atocCode"],
                    "atoc_name": service["atocName"],
                }

                cancelled_services.append(cancelled_service)

        return cancelled_services

    return []
