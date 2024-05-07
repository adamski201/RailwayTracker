"""Functions to load incident data into the RDS database"""

from psycopg2 import connect
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection


KEYS = ["created_at", "last_updated",
        "incident_number", "start_time",
        "end_time", "planned",
        "info_link", "routes_affected",
        "summary", "cleared"]

UPDATE_OR_INSERT_QUERY = """
    UPDATE incidents SET
    operator_id = %s,
    creation_date = %s,
    last_updated = %s,
    incident_uuid = %s,
    start_date = %s,
    end_date = %s,
    is_planned = %s,
    info_link = %s,
    affected_routes = %s,
    summary = %s,
    is_cleared = %s
    WHERE operator_id = %s AND incident_uuid = %s;
    INSERT INTO incidents (operator_id, creation_date, last_updated,
                    incident_uuid, start_date, end_date, is_planned,
                    info_link, affected_routes, summary, is_cleared)
    SELECT %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    WHERE NOT EXISTS (SELECT 1 FROM incidents WHERE operator_id = %s AND incident_uuid = %s);
    """


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


def get_values_for_insertion(data: dict) -> tuple:
    """Returns a tuple of all the data values to be inserted."""

    return tuple(data[key] for key in KEYS)


def insert_into_db(config: dict[str, str], val: tuple) -> None:
    """Inserts data into database as a new row if incident doesn't exist.
       Updates row if incident already exists."""

    conn = get_db_connection(config)
    with conn.cursor() as cur:
        cur.execute(UPDATE_OR_INSERT_QUERY, val)
        conn.commit()
        conn.close()


def get_operator_id(config: dict[str, str], operator_code: str, operator_name: str) -> int:
    """Retrieves relevant operator id from the database.
       If id doesn't exist, executes function to add and return operator id."""

    conn = get_db_connection(config)
    with conn.cursor() as cur:
        cur.execute("""SELECT operator_id FROM operators
                     WHERE operator_code = %s""", (operator_code,))
        op_id = cur.fetchone()
        if op_id:
            conn.close()
            return int(op_id["operator_id"])
        op_id = add_operator_id(config, operator_code, operator_name)
        return op_id


def add_operator_id(config: dict[str, str], operator_code: str, operator_name: str) -> int:
    """Adds operator code and name to database."""

    conn = get_db_connection(config)
    with conn.cursor() as cur:
        cur.execute("""INSERT INTO operators ("operator_name", "operator_code")
        VALUES (%s, %s)
        RETURNING operator_id;""", (operator_name, operator_code))
        conn.commit()
        op_id = cur.fetchone()
        conn.close()
        return int(op_id["operator_id"])


def load_data_to_database(config: dict[str, str], data: dict) -> None:
    """Prepares and loads incident data to database."""

    operators = dict(zip(data["operator_ref"], data["operator_name"]))
    incident_uuid = data["incident_number"]

    for operator_code, operator_name in operators.items():
        operator_id = get_operator_id(config, operator_code, operator_name)
        insert_values = (
            (operator_id,) + get_values_for_insertion(data) + (operator_id, incident_uuid))*2
        insert_into_db(config, insert_values)
