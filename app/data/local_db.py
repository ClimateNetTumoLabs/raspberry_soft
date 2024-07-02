import sqlite3
from typing import Union, Any

from logger_config import logging


class LocalDatabase:
    """
    Handles interactions with a local SQLite database.

    Attributes:
        db_name (str): Name of the database file.
        conn (sqlite3.Connection): Connection to the SQLite database.
        cursor (sqlite3.Cursor): Cursor for executing SQL commands.
        deviceID (str): Identifier for the device, used as table name.
        table_columns (dict): Mapping of column names to their SQLite data types.
    """

    def __init__(self, deviceID: str, db_name: str) -> None:
        """
        Initializes the LocalDatabase instance and connects to the database.

        Args:
            deviceID (str): Identifier for the device.
            db_name (str): Name of the database file.
        """
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.deviceID = f"device{deviceID}"
        self.table_columns = {
            "time": "TIMESTAMP",
            "uv": "REAL",
            "lux": "REAL",
            "temperature": "REAL",
            "pressure": "INTEGER",
            "humidity": "INTEGER",
            "pm1": "INTEGER",
            "pm2_5": "INTEGER",
            "pm10": "INTEGER",
            "speed": "REAL",
            "rain": "REAL",
            "direction": "TEXT"
        }

        self.connect_to_db()

    def connect_to_db(self) -> None:
        """
        Establishes a connection to the SQLite database.
        """
        try:
            connection = sqlite3.connect(self.db_name)
            cursor = connection.cursor()
            self.conn, self.cursor = connection, cursor
        except Exception as e:
            logging.error(f"Error occurred during connection to db: {str(e)}", exc_info=True)
            raise

    def create_table(self) -> None:
        """
        Creates a table in the database for storing device data.
        """
        try:
            column_definitions = [
                f"{column_name} {column_type}" for column_name, column_type in self.table_columns.items()
            ]
            query_columns = ",\n    ".join(column_definitions)

            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {self.deviceID} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        Drops the device table from the database.
        """
        try:
            self.cursor.execute(f"DROP TABLE IF EXISTS {self.deviceID}")
            self.conn.commit()
        except Exception as e:
            logging.error(f"Error occurred during dropping table {self.deviceID}: {str(e)}", exc_info=True)
            raise

    def get_data(self) -> list:
        """
        Retrieves all data from the device table.

        Returns:
            list: A list of dictionaries, each containing a row of data from the table.
        """
        try:
            self.cursor.execute(f"SELECT {', '.join(list(self.table_columns.keys()))} FROM {self.deviceID};")
            result = self.cursor.fetchall()
            columns = [desc[0] for desc in self.cursor.description]
            result = [dict(zip(columns, row)) for row in result]
            return result
        except Exception as e:
            logging.error(f"Error occurred during getting data from table {self.deviceID}: {str(e)}", exc_info=True)
            return []

    def insert_data(self, data: dict) -> None:
        """
        Inserts data into the device table.

        Args:
            data (dict): A dictionary containing the data to be inserted.
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
        Returns the number of rows in the device table.

        Returns:
            int: The number of rows in the table. Returns 0 if the table does not exist.
        """
        try:
            self.cursor.execute(f"SELECT COUNT(*) FROM {self.deviceID}")
            result = self.cursor.fetchone()
            return result[0]
        except sqlite3.OperationalError:
            return 0
