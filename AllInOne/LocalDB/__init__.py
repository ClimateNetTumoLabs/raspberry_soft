import psycopg2
import logging
from LocalDB.config import HOST, USERNAME, PASSWORD, DB_NAME
from logger_config import *


class LocalDatabase:
    """
    Class for interacting with a local PostgreSQL database.

    This class provides methods for connecting to a PostgreSQL database, creating and managing tables, and
    inserting and retrieving data from the database.

    Args:
        deviceID (str): The unique identifier for the device associated with the database.

    Methods:
        connect_to_db(self):
            Connect to the PostgreSQL database.

        create_table(self):
            Create a table in the database for storing sensor data.

        drop_table(self):
            Drop the table associated with the device from the database.

        get_data(self):
            Retrieve sensor data from the database.

        insert_data(self, data):
            Insert sensor data into the database.

    Attributes:
        deviceID (str): The unique identifier for the device.
        conn (psycopg2.extensions.connection): The database connection.
        cursor (psycopg2.extensions.cursor): The database cursor.
    """

    def __init__(self, deviceID) -> None:
        """
        Initialize the LocalDatabase class.

        This method initializes the LocalDatabase class, connects to the PostgreSQL database,
        and sets the deviceID.

        Args:
            deviceID (str): The unique identifier for the device associated with the database.

        Returns:
            None
        """
        self.connect_to_db()
        self.deviceID = deviceID

    def connect_to_db(self):
        """
        Connect to the PostgreSQL database.

        This method establishes a connection to the PostgreSQL database using the provided credentials
        and sets up a cursor for executing SQL queries.

        Returns:
            None
        """
        try:
            connection = psycopg2.connect(
                host=HOST,
                user=USERNAME,
                password=PASSWORD,
                database=DB_NAME
            )

            cursor = connection.cursor()

            self.conn, self.cursor = connection, cursor
        except Exception as e:
            logging.error(f"Error occurred during connection to db: {str(e)}", exc_info=True)
            raise

    def create_table(self):
        """
        Create a table in the database for storing sensor data.

        This method creates a table in the PostgreSQL database for storing sensor data.
        The table is named after the deviceID and includes columns for various sensor measurements.

        Returns:
            None
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

    def drop_table(self):
        """
        Drop the table associated with the device from the database.

        This method drops the table associated with the device from the PostgreSQL database.

        Returns:
            None
        """
        try:
            self.cursor.execute(f"DROP TABLE {self.deviceID}")
            self.conn.commit()
        except Exception as e:
            logging.error(f"Error occurred during dropping table {self.deviceID}: {str(e)}", exc_info=True)
            raise

    def get_data(self):
        """
        Retrieve sensor data from the database.

        This method retrieves sensor data from the database and returns it as a list of tuples.
        Each tuple contains the timestamp, light, temperature, pressure, humidity, PM1, PM2.5, PM10, wind speed,
        rain, and wind direction data.

        Returns:
            list: A list of tuples containing sensor data.
        """
        self.cursor.execute(f"SELECT time, light, temperature, pressure, humidity, PM1, PM2_5, PM10, speed, rain, direction FROM {self.deviceID};")

        result = self.cursor.fetchall()
        result = [(row[0].isoformat(), *row[1:]) for row in result]

        return result

    def insert_data(self, data):
        """
        Insert sensor data into the database.

        This method inserts sensor data into the PostgreSQL database for the associated device.
        The data is provided as a list and is inserted into the appropriate columns of the database table.

        Args:
            data (list): A list of sensor data including time, light, temperature, pressure, humidity, PM1, PM2.5, PM10, wind speed, rain, and wind direction.

        Returns:
            None
        """
        try:
            self.create_table()
            query_data = ', '.join([f"'{elem}'" if elem is not None else "NULL" for elem in data])
            self.cursor.execute(f"INSERT INTO {self.deviceID} (time, light, temperature, pressure, humidity, PM1, PM2_5, PM10, speed, rain, direction) VALUES ({query_data})")
            self.conn.commit()
        except Exception as e:
            logging.error(f"Error occurred during inserting data to Local DB: {str(e)}", exc_info=True)
            raise
