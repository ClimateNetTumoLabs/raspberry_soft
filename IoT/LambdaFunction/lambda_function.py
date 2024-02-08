import psycopg2
from config import host, user, password, db_name


columns = {
    "time": "TIMESTAMP",
    "light_vis": "REAL",
    "light_uv": "REAL",
    "light_ir": "REAL",
    "temperature": "REAL",
    "pressure": "REAL",
    "humidity": "REAL",
    "pm1": "REAL",
    "pm2_5": "REAL",
    "pm10": "REAL",
    "atm_pm1": "REAL",
    "atm_pm2_5": "REAL",
    "atm_pm10": "REAL",
    "litre_pm0_3": "REAL",
    "litre_pm0_5": "REAL",
    "litre_pm1": "REAL",
    "litre_pm2_5": "REAL",
    "litre_pm5": "REAL",
    "litre_pm10": "REAL",
    "speed": "REAL",
    "rain": "REAL",
    "direction": "TEXT"
}


def validate_value(value):
    try:
        if value is None:
            return "NULL"

        return f"'{round(float(value))}'"
    except ValueError:
        return f"'{value}'"


def connect_to_db(device_id):
    column_definitions = [f"{column_name} {column_type}" for column_name, column_type in columns.items()]
    query_columns = ",\n    ".join(column_definitions)

    create_table_query = f"""
CREATE TABLE IF NOT EXISTS {device_id} (
    id SERIAL PRIMARY KEY,
    {query_columns}
);
 """
    
    try:
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        )

        cursor = connection.cursor()

        cursor.execute(create_table_query)
        connection.commit()

        return connection, cursor

    except Exception as ex:
        print("Error", ex)
        return False


def add_message(info, connection, cursor):
    table_columns = list(columns.keys())

    device = info['device']

    for data in info['data']:
        fields = []
        values = []
        for key, value in data.items():
            if key in table_columns:
                fields.append(key)
                values.append(validate_value(value))

        cursor.execute(f"INSERT INTO {device} ({', '.join(fields)}) VALUES ({', '.join(values)})")

    connection.commit()


def lambda_handler(event, context):
    conn, cursor = connect_to_db(event["device"])

    add_message(event, conn, cursor)

    conn.close()
    return True

