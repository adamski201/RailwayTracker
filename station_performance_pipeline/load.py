from __future__ import annotations

from entities import Arrival, Operator, Station, Service
from psycopg2._psycopg import connection, cursor


def upload_arrivals(arrivals: list[Arrival], conn: connection) -> None:
    """
    Uploads transformed data to the specified database. Tries to obtain the keys of
    existing entities in the database; if it does not exist, uploads the entity.
    """
    cursor = conn.cursor()

    for arrival in arrivals:
        operator_id = get_operator_id(cursor, arrival.service.operator)
        if operator_id is None:
            operator_id = upload_operator(conn, cursor, arrival.service.operator)

        station_id = get_station_id(cursor, arrival.station)
        if station_id is None:
            station_id = upload_station(conn, cursor, arrival.station)

        service_id = get_service_id(cursor, arrival.service)
        if service_id is None:
            service_id = upload_service(conn, cursor, arrival.service, operator_id)

        upload_arrival(conn, cursor, arrival, station_id, service_id)

    conn.close()


def get_operator_id(cursor: cursor, operator: Operator) -> int | None:
    """
    Attempts to match the operator object to an existing entity in the database and extract
    its primary key. Otherwise, returns None.
    """
    cursor.execute(
        """
        SELECT OperatorId
        FROM Operators
        WHERE OperatorCode = %s;
        """,
        (operator.operator_code,),
    )

    res = cursor.fetchone()

    return res["OperatorId"] if res else None


def upload_operator(conn: connection, cursor: cursor, operator: Operator) -> int:
    """Uploads an operator object to the database, returning the new ID of the uploaded entity."""
    sql = """
        INSERT INTO Operators
            ("operatorname", "operatorcode")
        VALUES 
            (%s, %s);
          """

    params = (operator.operator_name, operator.operator_code)

    cursor.execute(sql, params)

    conn.commit()

    return int(cursor.lastrowid)


def get_station_id(cursor: cursor, station: Station):
    """
    Attempts to match the station object to an existing entity in the database and extract
    its primary key. Otherwise, returns None.
    """
    cursor.execute(
        """
        SELECT StationId
        FROM Stations
        WHERE StationName = %s;
        """,
        station.station_name,
    )

    res = cursor.fetchone()

    return res["StationId"] if res else None


def upload_station(conn: connection, cursor: cursor, station: Station) -> int:
    """Uploads a station object to the database, returning the new ID of the uploaded entity."""
    sql = """
        INSERT INTO Stations
            ("CrsCode", "StationName")
        VALUES 
            (%s, %s);
          """

    params = (station.crs_code, station.station_name)

    cursor.execute(sql, params)

    conn.commit()

    return int(cursor.lastrowid)


def get_service_id(cursor: cursor, service: Service):
    """
    Attempts to match the service object to an existing entity in the database and extract
    its primary key. Otherwise, returns None.
    """
    cursor.execute(
        """
        SELECT serviceid
        FROM Services
        WHERE serviceuuid = %s;
        """,
        service.service_uid,
    )

    res = cursor.fetchone()

    return res["ServiceId"] if res else None


def upload_service(
    conn: connection, cursor: cursor, service: Service, operator_id: int
) -> int:
    """Uploads a service object to the database, returning the new ID of the uploaded entity."""
    sql = """
        INSERT INTO Services
            ("OperatorId", "ServiceUUID")
        VALUES 
            (%s, %s);
          """

    params = (operator_id, service.service_uid)

    cursor.execute(sql, params)

    conn.commit()

    return int(cursor.lastrowid)


def upload_arrival(
    conn: connection, cursor: cursor, arrival: Arrival, station_id: int, service_id: int
) -> None:
    """Uploads an arrival object to the database."""
    sql = """
            INSERT INTO Arrivals
                ("StationId", "ServiceId", "ScheduledArrival", "ActualArrival")
            VALUES 
                (%s, %s, %s, %s);
              """

    params = (station_id, service_id, arrival.scheduled_arrival, arrival.actual_arrival)

    cursor.execute(sql, params)

    conn.commit()
