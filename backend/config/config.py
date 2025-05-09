from dotenv import load_dotenv
from pyaml_env import parse_config
from patterns import Singleton


load_dotenv()


class Config(metaclass=Singleton):
    def __init__(self) -> None:
        """
        Constructor of the class
        """
        try:
            self.conf = parse_config("config.yml", tag=None, default_value=None)
        except FileNotFoundError:
            print("Warning: Configuration file was not found, hence not parsed!")

    def get_database_connection_string(self):
        return self.conf["db"]["postgres"]["url"]

    def get_jwt_algorithm(self):
        return self.conf["auth"]["jwt"]["algorithm"]

    def get_secret_key(self):
        return self.conf["auth"]["jwt"]["secret"]

    def get_access_token_expire_minutes(self):
        return int(self.conf["auth"]["token"]["expiration"])

    def get_refresh_token_expire_minutes(self):
        return int(self.conf["auth"]["refresh_token"]["expiration"])

    def get_gutendex_base_url(self):
        return self.conf["general"]["gutendex_base_url"]
