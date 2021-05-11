import json
import os
import logging


guild_data_dictionary = None


def get_guild_data(guild_id) -> dict:
    """
    Returns a copy of a guild's data and creates new if necessary.
    """
    guild_id = str(guild_id)
    if guild_id not in guild_data_dictionary:
        # Initialize data for this guild
        guild_data_dictionary[guild_id] = {
            "keywords": {}
        }
    return guild_data_dictionary[guild_id].copy()


def set_guild_data(guild_id, new_data: dict, also_write_to_file: bool = True):
    """
    Overwrites a guild's data with new data.
    """
    guild_id = str(guild_id)
    guild_data_dictionary[guild_id] = new_data
    if also_write_to_file:
        write_to_file()


def write_to_file():
    keywords_json = json.dumps(guild_data_dictionary)
    with open("guild_data.json", "w") as guild_data_file:
        guild_data_file.write(keywords_json)


def load_from_file():
    global guild_data_dictionary

    if os.path.exists("guild_data.json"):
        with open("guild_data.json", "r") as data_file:
            guild_data_dictionary = json.loads(data_file.read())
    else:
        with open("guild_data.json", "w") as data_file:
            data_file.write("{}")
        guild_data_dictionary = {}


if guild_data_dictionary == None:
    load_from_file()