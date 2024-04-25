"""A module for uploading transformed data from the RTT API to a PSQL database."""

from __future__ import annotations

from psycopg2._psycopg import connection, cursor

from entities import Arrival, Operator, Station, Service, Cancellation, CancellationType


def upload_arrivals(arrivals: list[Arrival], conn: connection) -> None:
    """
    Uploads transformed arrival data to the specified database. Tries to obtain the keys of
    existing entities in the database; if it does not exist, uploads the entity.
    """
    cur = conn.cursor()

    for arrival in arrivals:
        station_id, service_id = upload_metadata(conn, cur, arrival)

        upload_arrival(conn, cur, arrival, station_id, service_id)


def upload_cancellations(cancellations: list[Cancellation], conn: connection) -> None:
    """
    Uploads transformed cancellation/arrival data to the specified database. Tries to
    obtain the keys of existing entities in the database; if it does not exist,
    uploads the entity.
    """
    cur = conn.cursor()

    for cancellation in cancellations:
        station_id, service_id = upload_metadata(conn, cur, cancellation)

        cancellation_type_id = get_cancellation_type_id(
            cur, cancellation.cancellation_type
        )
        if cancellation_type_id is None:
            cancellation_type_id = upload_cancellation_type(
                conn, cur, cancellation.cancellation_type
            )

        upload_cancellation(
            conn, cur, cancellation, station_id, service_id, cancellation_type_id
        )


def upload_metadata(conn: connection, cur: cursor, train) -> tuple:
    """
    Uploads train metadata - including operator, station, and service - if it does not
    already exist in the database, returning the new or existing IDs.
    """

    operator_id = get_operator_id(cur, train.service.operator)
    if operator_id is None:
        operator_id = upload_operator(conn, cur, train.service.operator)

    station_id = get_station_id(cur, train.station)
    if station_id is None:
        station_id = upload_station(conn, cur, train.station)

    service_id = get_service_id(cur, train.service)
    if service_id is None:
        service_id = upload_service(conn, cur, train.service, operator_id)

    return station_id, service_id


def get_operator_id(cur: cursor, operator: Operator) -> int | None:
    """
    Attempts to match the operator object to an existing entity in the database and extract
    its primary key. Otherwise, returns None.
    """
    cur.execute(
        """
        SELECT operator_id
        FROM operators
        WHERE operator_code = %s;
        """,
        (operator.operator_code,),
    )

    res = cur.fetchone()

    return res[0] if res else None


def upload_operator(conn: connection, cur: cursor, operator: Operator) -> int:
    """Uploads an operator object to the database, returning the new ID of the uploaded entity."""
    sql = """
        INSERT INTO operators
            ("operator_name", "operator_code")
        VALUES 
            (%s, %s)
        RETURNING operator_id;
          """

    params = (operator.operator_name, operator.operator_code)

    cur.execute(sql, params)

    conn.commit()

    return cursor.fetchone()[0]


def get_station_id(cur: cursor, station: Station):
    """
    Attempts to match the station object to an existing entity in the database and extract
    its primary key. Otherwise, returns None.
    """
    cur.execute(
        """
        SELECT station_id
        FROM stations
        WHERE station_name = %s;
        """,
        (station.station_name,),
    )

    res = cur.fetchone()

    return res[0] if res else None


def upload_station(conn: connection, cur: cursor, station: Station) -> int:
    """Uploads a station object to the database, returning the new ID of the uploaded entity."""
    sql = """
        INSERT INTO stations
            ("crs_code", "station_name")
        VALUES 
            (%s, %s)
        RETURNING
            station_id;
          """

    params = (station.crs_code, station.station_name)

    cur.execute(sql, params)

    conn.commit()

    return cursor.fetchone()[0]


def get_service_id(cur: cursor, service: Service):
    """
    Attempts to match the service object to an existing entity in the database and extract
    its primary key. Otherwise, returns None.
    """
    cur.execute(
        """
        SELECT service_id
        FROM services
        WHERE service_uid = %s;
        """,
        (service.service_uid,),
    )

    res = cur.fetchone()

    return res[0] if res else None


def upload_service(
    conn: connection, cur: cursor, service: Service, operator_id: int
) -> int:
    """Uploads a service object to the database, returning the new ID of the uploaded entity."""
    sql = """
        INSERT INTO services
            ("operator_id", "service_uid")
        VALUES 
            (%s, %s)
        RETURNING service_id;
          """

    params = (operator_id, service.service_uid)

    cur.execute(sql, params)

    conn.commit()

    return cur.fetchone()[0]


def upload_arrival(
    conn: connection, cur: cursor, arrival: Arrival, station_id: int, service_id: int
) -> None:
    """Uploads an arrival object to the database."""
    sql = """
            INSERT INTO arrivals
                ("station_id", "service_id", "scheduled_arrival", "actual_arrival")
            VALUES 
                (%s, %s, %s, %s);
              """

    params = (station_id, service_id, arrival.scheduled_arrival, arrival.actual_arrival)

    cur.execute(sql, params)

    conn.commit()


def get_cancellation_type_id(cur: cursor, cancellation_type: CancellationType):
    """
    Attempts to match the service object to an existing entity in the database and extract
    its primary key. Otherwise, returns None.
    """
    cur.execute(
        """
        SELECT cancellation_type_id
        FROM cancellation_types
        WHERE cancellation_code = %s;
        """,
        (cancellation_type.cancellation_code,),
    )

    res = cur.fetchone()

    return res[0] if res else None


def upload_cancellation_type(
    conn: connection, cur: cursor, cancellation_type: CancellationType
) -> int:
    """
    Uploads a cancellation type object to the database,
    returning the new ID of the uploaded entity.
    """
    sql = """
        INSERT INTO cancellation_types
            ("cancellation_code", "description")
        VALUES 
            (%s, %s)
        RETURNING cancellation_type_id;
          """

    params = (cancellation_type.cancellation_code, cancellation_type.description)

    cur.execute(sql, params)

    conn.commit()

    return cur.fetchone()[0]


def upload_cancellation(
    conn: connection,
    cur: cursor,
    cancellation: Cancellation,
    station_id: int,
    service_id: int,
    cancellation_type_id: int,
) -> None:
    """Uploads a cancellation object to the database."""
    sql = """
            INSERT INTO cancellations
                ("station_id", "service_id", "cancellation_type_id", "scheduled_arrival")
            VALUES 
                (%s, %s, %s, %s);
              """

    params = (
        station_id,
        service_id,
        cancellation_type_id,
        cancellation.scheduled_arrival,
    )

    cur.execute(sql, params)

    conn.commit()
