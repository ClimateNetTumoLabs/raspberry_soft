import psycopg2
from config import host, user, password, db_name


def connect_to_db(device_id):
    create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {device_id} (
            id SERIAL PRIMARY KEY,
            time TIMESTAMP,
            light REAL,
            temperature REAL,
            pressure REAL,
            humidity REAL,
            PM1 REAL,
            PM2_5 REAL,
            PM10 REAL,
            speed REAL,
            rain REAL,
            direction TEXT
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
    device = info['device']

    for data in info['data']:
        insert_data = ', '.join([f"'{elem}'" if elem is not None else "NULL" for elem in data])
        cursor.execute(f"INSERT INTO {device} (time, light, temperature, pressure, humidity, PM1, PM2_5, PM10, speed, rain, direction) VALUES ({insert_data})")
    
    connection.commit()


def lambda_handler(event, context):
    conn, cursor = connect_to_db(event["device"])
    
    add_message(event, conn, cursor)
    
    conn.close()
    return True
