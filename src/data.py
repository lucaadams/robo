import json


class Data:
    guild_data_dictionary = {}

    def __init__(self):
        self.load()

    def save(self):
        keywords_json = json.dumps(self.guild_data_dictionary)
        with open("guild_data.json", "w") as guild_data_file:
            guild_data_file.write(keywords_json)

    def load(self):
        with open("guild_data.json", "r") as guild_data_file:
            self.guild_data_dictionary = json.loads(guild_data_file.read())
    
    def get_guild_data(self, guild_id):
        guild_id = str(guild_id)
        if guild_id not in self.guild_data_dictionary:
            # Initialize data for this guild
            self.guild_data_dictionary[guild_id] = {
                "keywords": {}
            }
        return self.guild_data_dictionary[guild_id]

    def set_guild_data(self, guild_id, new_data: dict, also_save: bool = False):
        guild_id = str(guild_id)
        self.guild_data_dictionary[guild_id] = new_data
        if also_save: self.save()
