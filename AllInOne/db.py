import psycopg2
from config import HOST, USERNAME, PASSWORD, DB_NAME


class Database:
    def __init__(self) -> None:
        self.conn, self.cursor = self.connect_to_db()
        self.create_table()

    def connect_to_db(self):
        connection = psycopg2.connect(
            host=HOST,
            user=USERNAME,
            password=PASSWORD,
            database=DB_NAME
        )

        cursor = connection.cursor()

        print("Connected to database!!!")

        return connection, cursor

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS weather_data (
                id SERIAL PRIMARY KEY,
                time TIMESTAMP,
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

        print("Table Created!")
    
    def insert_data(self, data):
        values = ", ".join([f"'{elem}'" for elem in data])

        self.cursor.execute(f"""
            INSERT INTO weather_data (
                time, temperature, pressure, humidity, PM1, PM2_5, PM10, Atmospheric_PM1, 
                Atmospheric_PM2_5, Atmospheric_PM10, "0_3um", "0_5um", "1_0um", "2_5um", "5um", "10um", CO2, speed, rain, direction
            )
            VALUES ({values})""")
        self.conn.commit()

        print(f"Added values {values}")
