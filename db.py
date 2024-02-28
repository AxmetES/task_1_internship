import psycopg2
from config import settings


class DatabaseManager:
    def __init__(self, dbname=settings.POSTGRES_DB,
                 user=settings.POSTGRES_USER,
                 password=settings.POSTGRES_PASSWORD,
                 host=settings.POSTGRES_HOST,
                 port=settings.POSTGRES_PORT):
        self.conn_params = {
            'dbname': dbname,
            'user': user,
            'password': password,
            'host': host,
            'port': port
        }

    def __enter__(self):
        try:
            self.conn = psycopg2.connect(**self.conn_params)
            return self.conn.cursor()
        except psycopg2.Error as e:
            print(f"Error: Unable to connect to the database. {e}")
            raise

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.conn.commit()
        else:
            self.conn.rollback()

        self.conn.close()
