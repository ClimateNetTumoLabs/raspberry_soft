import json
import paho.mqtt.client as mqtt
import ssl
import psycopg2
from config import host, user, password, db_name


def connect_to_db():
    create_table_query = """
        CREATE TABLE IF NOT EXISTS messages (
            device TEXT,
            message TEXT
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
    mssg = info['message']
    
    cursor.execute(f"INSERT INTO messages (device, message) VALUES ('{device}', '{mssg}')")
    connection.commit()


def lambda_handler(event, context):
    conn, cursor = connect_to_db()
    
    add_message(event, conn, cursor)
    
    return True
