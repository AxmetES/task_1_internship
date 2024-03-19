import os

from environs import Env

env = Env()
env.read_env()


class Settings:
    def __init__(self):
        self.POSTGRES_DB = env.str("POSTGRES_DB")
        self.POSTGRES_USER = env.str("POSTGRES_USER")
        self.POSTGRES_PASSWORD = env.str("POSTGRES_PASSWORD")
        self.POSTGRES_PORT = env.str("POSTGRES_PORT")
        self.POSTGRES_HOST = env.str("POSTGRES_HOST")

        self.DB_CONN_URL = f'postgresql+psycopg2://{env.str("POSTGRES_USER")}:{env.str("POSTGRES_PASSWORD")}@{env.str("POSTGRES_HOST")}:{env.str("POSTGRES_PORT")}/{env.str("POSTGRES_DB")}'


settings = Settings()

os.makedirs("logs", exist_ok=True)
