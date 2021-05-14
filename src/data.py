import json
import os
import logging


GUILD_DATA_FILE_PATH = "guild_data.json"
__guild_data_dict = None


def get_guild_data(guild_id) -> dict:
    """
    Returns a copy of a guild's data and creates new if necessary.
    """
    guild_id = str(guild_id)
    if guild_id not in __guild_data_dict:
        # Initialize data for this guild
        __guild_data_dict[guild_id] = {
            "keywords": {},
            "saved_queues": {}
        }
    return __guild_data_dict[guild_id].copy()


def set_guild_data(guild_id, new_data: dict, also_write_to_file: bool = True):
    """
    Overwrites a guild's data with new data.
    """
    guild_id = str(guild_id)
    __guild_data_dict[guild_id] = new_data
    if also_write_to_file:
        write_to_file()


def write_to_file():
    keywords_json = json.dumps(__guild_data_dict)
    with open(GUILD_DATA_FILE_PATH, "w") as guild_data_file:
        guild_data_file.write(keywords_json)
    logging.info(f"Data was written to {GUILD_DATA_FILE_PATH}")


def load_from_file():
    global __guild_data_dict

    if os.path.exists(GUILD_DATA_FILE_PATH):
        with open(GUILD_DATA_FILE_PATH, "r") as data_file:
            __guild_data_dict = json.loads(data_file.read())
    else:
        with open(GUILD_DATA_FILE_PATH, "w") as data_file:
            data_file.write("{}")
        __guild_data_dict = {}


if __guild_data_dict is None:
    load_from_file()
