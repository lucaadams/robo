import json
import os
import logging


class DataManager:
    def __init__(self):
        APPDATA_FILE_PATH = os.getenv("APPDATA") or "."
        self.ROOT_FILE_PATH = os.path.realpath(__file__).strip("src\data.py")

        if not os.path.exists(f"{APPDATA_FILE_PATH}/robo-test"):
            os.mkdir(f"{APPDATA_FILE_PATH}/robo-test")

        self.GUILD_DATA_FILE_PATH = f"{APPDATA_FILE_PATH}/robo-test/guild_data.json"

        if os.path.exists(self.GUILD_DATA_FILE_PATH):
            with open(self.GUILD_DATA_FILE_PATH, "r") as data_file:
                self.__guild_data_dict = json.loads(data_file.read())
        else:
            with open(self.GUILD_DATA_FILE_PATH, "w") as data_file:
                data_file.write("{}")
            self.__guild_data_dict = {}


    def get_guild_data(self, guild_id) -> dict:
        """
        Returns a copy of a guild's data and creates new if necessary.
        """
        guild_id = str(guild_id)
        if guild_id not in self.__guild_data_dict:
            # Initialize data for this guild
            self.__guild_data_dict[guild_id] = {
                "keywords": {},
                "saved_queues": {}
            }
        return self.__guild_data_dict[guild_id].copy()


    def set_guild_data(self, guild_id, new_data: dict, also_write_to_file: bool = True):
        """
        Overwrites a guild's data with new data.
        """
        guild_id = str(guild_id)
        self.__guild_data_dict[guild_id] = new_data
        if also_write_to_file:
            self.write_to_file()


    def write_to_file(self):
        keywords_json = json.dumps(self.__guild_data_dict)
        with open(self.GUILD_DATA_FILE_PATH, "w") as guild_data_file:
            guild_data_file.write(keywords_json)
        logging.info(f"Data was written to {self.GUILD_DATA_FILE_PATH}")


    def load_from_file(self):
        if os.path.exists(self.GUILD_DATA_FILE_PATH):
            with open(self.GUILD_DATA_FILE_PATH, "r") as data_file:
                self.__guild_data_dict = json.loads(data_file.read())
        else:
            with open(self.GUILD_DATA_FILE_PATH, "w") as data_file:
                data_file.write("{}")
            self.__guild_data_dict = {}


data = DataManager()

