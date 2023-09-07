import psycopg2
import logging
from config import HOST, USERNAME, PASSWORD, DB_NAME


logging.basicConfig(filename='parsing.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Database:
    def connect_to_db(self):
        try:
            connection = psycopg2.connect(
                host=HOST,
                user=USERNAME,
                password=PASSWORD,
                database=DB_NAME
            )

            cursor = connection.cursor()

            self.conn, self.cursor = connection, cursor

            logging.info("Successfully connected to db")

        except Exception as e:
            logging.error(f"Error occurred during connection to db: {str(e)}", exc_info=True)
            raise

    def create_table(self):
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS weather_data (
                    id SERIAL PRIMARY KEY,
                    time TIMESTAMP,
                    light REAL,
                    temperature REAL,
                    pressure REAL,
                    humidity REAL,
                    PM1 REAL,
                    PM2_5 REAL,
                    PM10 REAL,
                    Atmospheric_PM1 REAL,
                    Atmospheric_PM2_5 REAL,
                    Atmospheric_PM10 REAL,
                    "0_3um" REAL,
                    "0_5um" REAL,
                    "1_0um" REAL,
                    "2_5um" REAL,
                    "5um" REAL,
                    "10um" REAL,
                    CO2 REAL,
                    speed REAL,
                    rain REAL,
                    direction TEXT
                );
            """)

            self.conn.commit()

            logging.info("Successfully created table weather_data")
        except Exception as e:
            logging.error(f"Error occurred during creating table weather_data: {str(e)}", exc_info=True)
            raise
    
    def insert_data(self, data):
        try:
            values = ", ".join([f"'{elem}'" if elem is not None else "NULL" for elem in data])

            self.cursor.execute(f"""
                INSERT INTO weather_data (
                    time, light, temperature, pressure, humidity, PM1, PM2_5, PM10, Atmospheric_PM1, 
                    Atmospheric_PM2_5, Atmospheric_PM10, "0_3um", "0_5um", "1_0um", "2_5um", "5um", "10um", CO2, speed, rain, direction
                )
                VALUES ({values})""")
            self.conn.commit()

            logging.info("Successfully inserted data into the database")
        except Exception as e:
            logging.error(f"Error occurred during creating table weather_data: {str(e)}", exc_info=True)
            raise
