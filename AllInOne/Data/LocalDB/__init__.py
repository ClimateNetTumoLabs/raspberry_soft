from typing import Union, Any
import psycopg2
from Data.config import LOCAL_DB_HOST, LOCAL_DB_USERNAME, LOCAL_DB_PASSWORD, LOCAL_DB_DB_NAME
from logger_config import *


class LocalDatabase:
    def __init__(self, deviceID: str) -> None:
        """
        Initializes a LocalDatabase instance.

        Args:
            deviceID (str): The unique identifier for the device associated with the database.

        Returns:
            None
        """
        self.conn = None
        self.cursor = None
        self.connect_to_db()
        self.deviceID = deviceID

        self.table_columns = ["time", "light_vis", "light_uv", "light_ir", "temperature", "pressure", "humidity", "pm1",
                              "pm2_5", "pm10", "atm_pm1", "atm_pm2_5", "atm_pm10", "litre_pm0_3", "litre_pm0_5",
                              "litre_pm1", "litre_pm2_5", "litre_pm5", "litre_pm10", "speed", "rain", "direction"]

    def connect_to_db(self) -> None:
        """
        Establishes a connection to the local PostgreSQL database.

        Args:
            None

        Returns:
            None
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
        Creates a table in the database if it does not already exist.

        Args:
            None

        Returns:
            None
        """
        try:
            self.cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.deviceID} (
                    id SERIAL PRIMARY KEY,
                    time TIMESTAMP,
                    light_vis SMALLINT,
                    light_uv REAL,
                    light_ir SMALLINT,
                    temperature SMALLINT,
                    pressure SMALLINT,
                    humidity SMALLINT,
                    pm1 SMALLINT,
                    pm2_5 SMALLINT,
                    pm10 SMALLINT,
                    atm_pm1 SMALLINT,
                    atm_pm2_5 SMALLINT,
                    atm_pm10 SMALLINT,
                    litre_pm0_3 SMALLINT,
                    litre_pm0_5 SMALLINT,
                    litre_pm1 SMALLINT,
                    litre_pm2_5 SMALLINT,
                    litre_pm5 SMALLINT,
                    litre_pm10 SMALLINT,
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
        Drops the table associated with the deviceID from the database.

        Args:
            None

        Returns:
            None
        """
        try:
            self.cursor.execute(f"DROP TABLE {self.deviceID}")
            self.conn.commit()
        except Exception as e:
            logging.error(f"Error occurred during dropping table {self.deviceID}: {str(e)}", exc_info=True)
            raise

    def get_data(self) -> list:
        """
        Retrieves data from the database associated with the deviceID.

        Args:
            None

        Returns:
            list: A list of dictionaries containing the retrieved data.
        """
        self.cursor.execute(f"SELECT {', '.join(self.table_columns)} FROM {self.deviceID};")

        result = self.cursor.fetchall()
        columns = [desc[0] for desc in self.cursor.description]

        result = [dict(zip(columns, row)) for row in [(row[0].isoformat(), *row[1:]) for row in result]]

        return result

    def insert_data(self, data: dict) -> None:
        """
        Inserts data into the database associated with the deviceID.

        Args:
            data (dict): A dictionary containing the data to be inserted.

        Returns:
            None
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

    def get_count(self) -> Union[int, Any]:
        """
        Retrieves the count of records in the table associated with the deviceID.

        Args:
            None

        Returns:
            Union[int, Any]: The count of records if the table exists, otherwise returns 0.
        """
        try:
            self.cursor.execute(f"SELECT COUNT(*) FROM {self.deviceID}")

            result = self.cursor.fetchall()

            return result[0][0]
        except psycopg2.errors.UndefinedTable:
            return 0
