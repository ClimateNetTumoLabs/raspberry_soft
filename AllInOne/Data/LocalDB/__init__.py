"""
    Database interaction module for a local PostgreSQL database.

    This module provides a class, LocalDatabase, for connecting to and interacting with a PostgreSQL database.
    The class includes methods for creating a table, dropping a table, retrieving data, and inserting data.

    Class Docstring:
    ----------------
    LocalDatabase:
        Represents a connection to a PostgreSQL database with methods for table management and data operations.

    Constructor Args:
        deviceID (str): Identifier for the device, used as the table name in the database.

    Class Attributes:
        conn (psycopg2.extensions.connection): Connection to the PostgreSQL database.
        cursor (psycopg2.extensions.cursor): Database cursor for executing SQL queries.
        deviceID (str): Identifier for the device, used as the table name in the database.

    Methods:
        __init__(self, deviceID: str):
            Initializes a LocalDatabase object and connects to the PostgreSQL database.

        connect_to_db(self):
            Establishes a connection to the PostgreSQL database using configuration parameters.

        create_table(self):
            Creates a table in the database with columns for various sensor data types.

        drop_table(self):
            Drops the table associated with the deviceID.

        get_data(self) -> list:
            Retrieves all data from the table associated with the deviceID.

        insert_data(self, data: dict):
            Inserts sensor data into the table associated with the deviceID.

        Module Usage:
        -------------
        To use this module, create an instance of the LocalDatabase class, passing the deviceID as an argument.
        Use the various methods to manage tables and perform data operations on the PostgreSQL database.
"""

import psycopg2
from Data.config import LOCAL_DB_HOST, LOCAL_DB_USERNAME, LOCAL_DB_PASSWORD, LOCAL_DB_DB_NAME
from logger_config import *


class LocalDatabase:
    """
    Represents a connection to a PostgreSQL database with methods for table management and data operations.

    Attributes:
        conn (psycopg2.extensions.connection): Connection to the PostgreSQL database.
        cursor (psycopg2.extensions.cursor): Database cursor for executing SQL queries.
        deviceID (str): Identifier for the device, used as the table name in the database.
    """
    def __init__(self, deviceID: str) -> None:
        """
        Initializes a LocalDatabase object and connects to the PostgreSQL database.

        Args:
            deviceID (str): Identifier for the device, used as the table name in the database.
        """
        self.conn = None
        self.cursor = None
        self.connect_to_db()
        self.deviceID = deviceID

    def connect_to_db(self) -> None:
        """
        Establishes a connection to the PostgreSQL database using configuration parameters.

        Raises:
            Exception: Logs an error and raises an exception if the connection attempt fails.
        """
        try:
            connection = psycopg2.connect(
                host=LOCAL_DB_HOST,
                user=LOCAL_DB_USERNAME,
                password=LOCAL_DB_PASSWORD,
                database=LOCAL_DB_DB_NAME
            )

            cursor = connection.cursor()

            self.conn, self.cursor = connection, cursor
        except Exception as e:
            logging.error(f"Error occurred during connection to db: {str(e)}", exc_info=True)
            raise

    def create_table(self) -> None:
        """
        Creates a table in the database with columns for various sensor data types.

        Raises:
            Exception: Logs an error and raises an exception if the table creation fails.
        """
        try:
            self.cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.deviceID} (
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
                """)

            self.conn.commit()
        except Exception as e:
            logging.error(f"Error occurred during creating table {self.deviceID}: {str(e)}", exc_info=True)
            raise

    def drop_table(self) -> None:
        """
        Drops the table associated with the deviceID.

        Raises:
            Exception: Logs an error and raises an exception if the table dropping fails.
        """
        try:
            self.cursor.execute(f"DROP TABLE {self.deviceID}")
            self.conn.commit()
        except Exception as e:
            logging.error(f"Error occurred during dropping table {self.deviceID}: {str(e)}", exc_info=True)
            raise

    def get_data(self) -> list:
        """
        Retrieves all data from the table associated with the deviceID.

        Returns:
            list: A list of tuples representing rows of data, each tuple includes timestamp and various sensor readings.
        """
        self.cursor.execute(f"SELECT time, light, temperature, pressure, humidity, PM1, PM2_5, PM10, speed, rain, "
                            f"direction FROM {self.deviceID};")

        result = self.cursor.fetchall()
        result = [(row[0].isoformat(), *row[1:]) for row in result]

        return result

    def insert_data(self, data: dict) -> None:
        """
        Inserts sensor data into the table associated with the deviceID.

        Args:
            data (dict): A dictionary containing sensor readings to be inserted into the database.

        Raises:
            Exception: Logs an error and raises an exception if the data insertion fails.
        """
        try:
            self.create_table()
            query_data = ', '.join([f"'{elem}'" if elem is not None else "NULL" for elem in data.values()])
            self.cursor.execute(f"INSERT INTO {self.deviceID} (time, light, temperature, pressure, humidity, PM1, "
                                f"PM2_5, PM10, speed, rain, direction) VALUES ({query_data})")
            self.conn.commit()
        except Exception as e:
            logging.error(f"Error occurred during inserting data to Local DB: {str(e)}", exc_info=True)
            raise
