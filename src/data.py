import json


guild_data_dictionary = {}


def save():
    keywords_json = json.dumps(guild_data_dictionary)
    with open("guild_data.json", "w") as guild_data_file:
        guild_data_file.write(keywords_json)


def load():
    global guild_data_dictionary
    with open("guild_data.json", "r") as guild_data_file:
        guild_data_dictionary = json.loads(guild_data_file.read())


def get_guild_data(guild_id):
    guild_id = str(guild_id)
    if guild_id not in guild_data_dictionary:
        # Initialize data for this guild
        guild_data_dictionary[guild_id] = {
            "keywords": {}
        }
    return guild_data_dictionary[guild_id]


def set_guild_data(guild_id, new_data: dict, also_save: bool = False):
    guild_id = str(guild_id)
    guild_data_dictionary[guild_id] = new_data
    if also_save:
        save()
