from typing import Union, Any
import psycopg2
from Data.config import LOCAL_DB_HOST, LOCAL_DB_USERNAME, LOCAL_DB_PASSWORD, LOCAL_DB_DB_NAME
from logger_config import *


class LocalDatabase:
    """
    A class for interacting with a local PostgreSQL database.

    Attributes:
        conn: Connection to the database.
        cursor: Cursor for executing SQL commands.
        deviceID (str): Identifier for the device associated with the database.

    Methods:
        connect_to_db: Establishes a connection to the local database.
        create_table: Creates a table in the database.
        drop_table: Drops a table from the database.
        get_data: Retrieves data from the database.
        insert_data: Inserts data into the database.
        get_count: Retrieves the count of records in the database.
    """

    def __init__(self, deviceID: str) -> None:
        """
        Initializes the LocalDatabase object.

        Args:
            deviceID (str): Identifier for the device associated with the database.
        """
        self.conn = None
        self.cursor = None
        self.connect_to_db()
        self.deviceID = deviceID

        self.table_columns = {
            "time": "TIMESTAMP",
            "light_vis": "SMALLINT",
            "light_uv": "REAL",
            "light_ir": "SMALLINT",
            "temperature": "SMALLINT",
            "pressure": "SMALLINT",
            "humidity": "SMALLINT",
            "pm1": "SMALLINT",
            "pm2_5": "SMALLINT",
            "pm10": "SMALLINT",
            "atm_pm1": "SMALLINT",
            "atm_pm2_5": "SMALLINT",
            "atm_pm10": "SMALLINT",
            "litre_pm0_3": "SMALLINT",
            "litre_pm0_5": "SMALLINT",
            "litre_pm1": "SMALLINT",
            "litre_pm2_5": "SMALLINT",
            "litre_pm5": "SMALLINT",
            "litre_pm10": "SMALLINT",
            "speed": "REAL",
            "rain": "REAL",
            "direction": "TEXT"
        }

    def connect_to_db(self) -> None:
        """
        Establishes a connection to the local database.
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
        Creates a table in the database.
        """
        try:
            column_definitions = [f"{column_name} {column_type}" for column_name, column_type in self.table_columns.items()]
            query_columns = ",\n    ".join(column_definitions)

            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {self.deviceID} (
                id SERIAL PRIMARY KEY,
                {query_columns}
            );
             """

            self.cursor.execute(create_table_query)

            self.conn.commit()
        except Exception as e:
            logging.error(f"Error occurred during creating table {self.deviceID}: {str(e)}", exc_info=True)
            raise

    def drop_table(self) -> None:
        """
        Drops a table from the database.
        """
        try:
            self.cursor.execute(f"DROP TABLE {self.deviceID}")
            self.conn.commit()
        except Exception as e:
            logging.error(f"Error occurred during dropping table {self.deviceID}: {str(e)}", exc_info=True)
            raise

    def get_data(self) -> list:
        """
        Retrieves data from the database.

        Returns:
            list: A list of dictionaries containing the retrieved data.
        """
        self.cursor.execute(f"SELECT {', '.join(list(self.table_columns.keys()))} FROM {self.deviceID};")

        result = self.cursor.fetchall()
        columns = [desc[0] for desc in self.cursor.description]

        result = [dict(zip(columns, row)) for row in [(row[0].isoformat(), *row[1:]) for row in result]]

        return result

    def insert_data(self, data: dict) -> None:
        """
        Inserts data into the database.

        Args:
            data (dict): A dictionary containing data to be inserted into the database.
        """
        try:
            self.create_table()

            table_columns = list(self.table_columns.keys())

            fields = []
            values = []
            for key, value in data.items():
                if key in table_columns:
                    fields.append(key)
                    values.append(f"'{value}'" if value is not None else "NULL")

            self.cursor.execute(f"INSERT INTO {self.deviceID} ({', '.join(fields)}) VALUES ({', '.join(values)})")

            self.conn.commit()
        except Exception as e:
            logging.error(f"Error occurred during inserting data to Local DB: {str(e)}", exc_info=True)
            raise

    def get_count(self) -> Union[int, Any]:
        """
        Retrieves the count of records in the database.

        Returns:
            Union[int, Any]: The count of records in the database, or 0 if the table does not exist.
        """
        try:
            self.cursor.execute(f"SELECT COUNT(*) FROM {self.deviceID}")

            result = self.cursor.fetchall()

            return result[0][0]
        except psycopg2.errors.UndefinedTable:
            return 0
