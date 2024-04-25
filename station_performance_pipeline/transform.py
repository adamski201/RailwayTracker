from entities import Arrival, Cancellation, Operator, Station, Service, CancellationType

from datetime import date, datetime


def transform_train_services_data(train_services: list[dict], date: date):
    """This function accepts a list of dictionaries corresponding to the trains that
    arrived, or were expected to arrive, at a specific station and returns another
    list of dictionaries.
    Each dictionary represents a train that arrived at the station on this day,
    extracting only relevant data from the inputted list.
    The dictionary has the keys related to the expected and actual times of arrival
    and departure."""

    if not train_services:
        raise ValueError(f"No services for provided station.")

    station = Station(
        crs_code=train_services[0]["locationDetail"]["crs"],
        station_name=train_services[0]["locationDetail"]["description"],
    )

    arrivals = []
    cancellations = []
    for service in train_services:
        if service["serviceType"] != "train":
            continue

        try:
            operator = Operator(
                operator_name=service["atocName"], operator_code=service["atocCode"]
            )

            train_service = Service(
                operator=operator, service_uid=service["serviceUid"]
            )

            if "cancelReasonCode" in service["locationDetail"].keys():
                cancellation_type = CancellationType(
                    cancellation_code=service["locationDetail"]["cancelReasonCode"],
                    description=service["locationDetail"]["cancelReasonLongText"],
                )

                if "gbttBookedArrival" in service["locationDetail"]:
                    scheduled_time = get_datetime_from_time_str(
                        date, service["locationDetail"]["gbttBookedArrival"]
                    )
                else:
                    scheduled_time = get_datetime_from_time_str(
                        date, service["locationDetail"]["gbttBookedDeparture"]
                    )

                cancellations.append(
                    Cancellation(
                        cancellation_type=cancellation_type,
                        station=station,
                        service=train_service,
                        scheduled_arrival=scheduled_time,
                    )
                )
            else:
                if (
                    "gbttBookedArrival" in service["locationDetail"]
                    and "realtimeArrival" in service["locationDetail"]
                ):
                    scheduled_time = get_datetime_from_time_str(
                        date, service["locationDetail"]["gbttBookedArrival"]
                    )
                    actual_time = get_datetime_from_time_str(
                        date, service["locationDetail"]["realtimeArrival"]
                    )
                else:
                    scheduled_time = get_datetime_from_time_str(
                        date, service["locationDetail"]["gbttBookedDeparture"]
                    )
                    actual_time = get_datetime_from_time_str(
                        date, service["locationDetail"]["realtimeDeparture"]
                    )

                arrivals.append(
                    Arrival(
                        station=station,
                        service=train_service,
                        scheduled_arrival=scheduled_time,
                        actual_arrival=actual_time,
                    )
                )
        except KeyError as e:
            print(
                f"KeyError: Missing {e} for service {service['serviceUid']} at station {station.station_name}."
            )

    return arrivals, cancellations


def get_datetime_from_time_str(date: date, time: str) -> datetime:
    return datetime.combine(date, datetime.strptime(time, "%H%M").time())
