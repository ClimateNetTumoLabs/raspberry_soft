import sqlite3
from typing import Union, Any

from logger_config import logging


class LocalDatabase:
    def __init__(self, deviceID: str, db_name: str) -> None:
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
        try:
            connection = sqlite3.connect(self.db_name)
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
        try:
            self.cursor.execute(f"DROP TABLE IF EXISTS {self.deviceID}")
            self.conn.commit()
        except Exception as e:
            logging.error(f"Error occurred during dropping table {self.deviceID}: {str(e)}", exc_info=True)
            raise

    def get_data(self) -> list:
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
        try:
            self.cursor.execute(f"SELECT COUNT(*) FROM {self.deviceID}")
            result = self.cursor.fetchone()
            return result[0]
        except sqlite3.OperationalError:
            return 0
