import discord
import json

import text_module.embeds


with open("guild_data.json", "r") as guild_data_file:
    guild_data_dictionary = json.loads(guild_data_file.read())


async def add(guild_id, message, keyword, value):
    await init_new_guild(guild_id)
    if value == "":
        await message.channel.send(embed=await text_module.embeds.embed_error_message("No value specified. "))
    else:
        guild_data_dictionary[guild_id]["keywords"][keyword] = value
        await message.channel.send(embed=await text_module.embeds.embed_successful_action("Keyword added. "))

    await save_keywords()


async def remove(guild_id, message, keyword):
    await init_new_guild(guild_id)
    message_removal = message.content.split(" ")[2]
    guild_data_dictionary[guild_id]["keywords"].pop(message_removal)
    await message.channel.send(embed=await text_module.embeds.embed_successful_action("Keyword removed. "))

    await save_keywords()


async def edit(guild_id, message, old_keyword, new_keyword):
    await init_new_guild(guild_id)
    guild_data_dictionary[guild_id]["keywords"][new_keyword] = guild_data_dictionary[guild_id]["keywords"].pop(
        old_keyword)
    await message.channel.send(embed=await text_module.embeds.embed_successful_action("Keyword edited. "))

    await save_keywords()


async def list(guild_id, message):
    keywords_list = ""
    await init_new_guild(guild_id)
    for keyword in guild_data_dictionary[guild_id]["keywords"]:
        keywords_list += f"• `{keyword} - {guild_data_dictionary[guild_id]['keywords'][keyword]}`\n"

    if keywords_list == "":
        await message.channel.send(embed=await text_module.embeds.embed_response("No keywords set.", "Nothing to display."))
    else:
        await message.channel.send(embed=await text_module.embeds.embed_response("Keywords:", f"{keywords_list}"))


async def save_keywords():
    keywords_json = json.dumps(guild_data_dictionary)
    with open("guild_data.json", "w") as keywords_file:
        keywords_file.write(keywords_json)


async def check_keywords(guild_id, message):
    await init_new_guild(guild_id)
    for keyword in guild_data_dictionary[guild_id]["keywords"].keys():
        if message.content.__contains__(keyword):
            await message.channel.send(guild_data_dictionary[guild_id]["keywords"][keyword])
            return


async def init_new_guild(guild_id):
    if guild_id not in guild_data_dictionary:
        guild_data_dictionary[guild_id] = {
            "keywords": {}
        }
