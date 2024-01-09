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

        self.table_columns = ["time", "light", "temperature", "pressure", "humidity", "pm1", "pm2_5", "pm10",
                              "atm_pm1", "atm_pm2_5", "atm_pm10", "litre_pm0_3", "litre_pm0_5", "litre_pm1",
                              "litre_pm2_5", "litre_pm5", "litre_pm10", "speed", "rain", "direction"]

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
                    pm1 REAL,
                    pm2_5 REAL,
                    pm10 REAL,
                    atm_pm1 REAL,
                    atm_pm2_5 REAL,
                    atm_pm10 REAL,
                    litre_pm0_3 REAL,
                    litre_pm0_5 REAL,
                    litre_pm1 REAL,
                    litre_pm2_5 REAL,
                    litre_pm5 REAL,
                    litre_pm10 REAL,
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
            list: A list of dicts representing rows of data, each dict includes timestamp and various sensor readings.
        """
        self.cursor.execute(f"SELECT {', '.join(self.table_columns)} FROM {self.deviceID};")

        result = self.cursor.fetchall()
        columns = [desc[0] for desc in self.cursor.description]

        result = [dict(zip(columns, row)) for row in [(row[0].isoformat(), *row[1:]) for row in result]]

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

            fields = []
            values = []
            for key, value in data.items():
                if key in self.table_columns:
                    fields.append(key)
                    values.append(f"'{value}'" if value is not None else "NULL")

            self.cursor.execute(f"INSERT INTO {self.deviceID} ({', '.join(fields)}) VALUES ({', '.join(values)})")

            self.conn.commit()
        except Exception as e:
            logging.error(f"Error occurred during inserting data to Local DB: {str(e)}", exc_info=True)
            raise
    
    def get_count(self) -> list:
        try:
            self.cursor.execute(f"SELECT COUNT(*) FROM {self.deviceID}")

            result = self.cursor.fetchall()

            return result[0][0]
        except psycopg2.errors.UndefinedTable:
            return 0
