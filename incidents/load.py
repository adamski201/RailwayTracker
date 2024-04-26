"""Load functions to load incident data into the database"""

from psycopg2 import connect
from psycopg2.extensions import connection
from psycopg2.extras import RealDictCursor


def get_db_connection(config: dict[str, str]) -> connection:
    """Returns a connection to the database."""

    return connect(
        dbname=config["DB_NAME"],
        user=config.get("DB_USER"),
        password=config.get("DB_PASS"),
        host=config.get("DB_HOST"),
        port=config.get("DB_PORT", 5432),
        cursor_factory=RealDictCursor
    )


def get_values_for_insertion(data: list[dict]) -> tuple:
    """Returns a tuple of all the data values to be inserted"""

    return tuple(data[0][key] for key in ["created_at", "last_updated",
                                          "incident_number", "start_time",
                                          "end_time", "planned",
                                          "info_link", "routes_affected",
                                          "summary", "description"])


def insert_into_db(config: dict[str, str], val: tuple) -> None:
    """Inserts data into database"""

    conn = get_db_connection(config)
    with conn.cursor() as cur:
        cur.execute("""INSERT INTO incidents (operator_id, creation_date, last_updated,
                    incident_uuid, start_date, end_date, planned,
                    info_link, affected_routes, summary, description)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", val)
        conn.commit()
        conn.close()


def get_operator_id(config: dict[str, str], data: list[dict]) -> int:
    """Retrieves relevant operator id from the database"""

    operator_code = data[0]["operator_ref"]
    conn = get_db_connection(config)
    with conn.cursor() as cur:
        cur.execute("""SELECT operator_id FROM operators
                     WHERE operator_code = %s""", (operator_code,))
        op_id = cur.fetchone()["operator_id"]
        conn.close()
        return int(op_id)


def load_to_database(config: dict[str, str], data: list[dict]) -> None:
    """Prepares and loads incident data to database"""

    operator_id = get_operator_id(config, data)
    values = (operator_id,) + get_values_for_insertion(data)
    insert_into_db(config, values)
