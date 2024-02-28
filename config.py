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


settings = Settings()