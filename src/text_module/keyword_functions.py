import random
import discord

import data
import text_module.embeds


async def command_handler(message):
    guild_id = message.guild.id
    second_parameter = message.content.split(" ")[2]

    if second_parameter == "add":
        await add(guild_id, message, message.content.split(" ")[3], " ".join(message.content.split(" ")[4:]))

    elif second_parameter == "remove":
        try:
            await remove(guild_id, message, message.content.split(" ")[3])
        except:
            await message.channel.send(embed=text_module.embeds.embed_error_message("That keyword does not exist. Did you make a typo? "))

    elif second_parameter == "edit":
        try:
            if message.content.split(" ")[3] == "":
                await message.channel.send(embed=text_module.embeds.embed_error_message("Name of new keyword must be specified. "))
            else:
                await edit(guild_id, message, message.content.split(" ")[3], " ".join(message.content.split(" ")[4:]))
        except:
            await message.channel.send(embed=text_module.embeds.embed_error_message("That keyword does not exist. Did you make a typo? "))

    elif second_parameter == "list":
        await list_keywords(guild_id, message)


async def add(guild_id, message, keyword, value):
    guild_data = data.get_guild_data(guild_id)
    if value == "":
        await message.channel.send(embed=text_module.embeds.embed_error_message("No value specified. "))
    else:
        if keyword in guild_data["keywords"]:
            guild_data["keywords"][keyword].append(value)
        else:
            guild_data["keywords"][keyword] = [value]
        await message.channel.send(embed=text_module.embeds.embed_successful_action("Keyword added. "))
    data.set_guild_data(guild_id, guild_data)


async def remove(guild_id, message, message_removal):
    guild_data = data.get_guild_data(guild_id)
    guild_data["keywords"].pop(message_removal)
    await message.channel.send(embed=text_module.embeds.embed_successful_action("Keyword removed. "))

    data.set_guild_data(guild_id, guild_data)


async def edit(guild_id, message, old_keyword, new_keyword):
    guild_data = data.get_guild_data(guild_id)
    guild_data["keywords"][new_keyword] = guild_data["keywords"].pop(
        old_keyword)
    await message.channel.send(embed=text_module.embeds.embed_successful_action("Keyword edited. "))

    data.set_guild_data(guild_id, guild_data)


async def list_keywords(guild_id, message):
    guild_data = data.get_guild_data(guild_id)
    keywords_list = ""
    for keyword in guild_data["keywords"]:
        keyword_values_str = ""
        for value in guild_data['keywords'][keyword]:
            keyword_values_str += value + ", "
        keyword_values_str = keyword_values_str.strip(", ")
        keywords_list += f"• `{keyword} - {keyword_values_str}`\n"

    if keywords_list == "":
        await message.channel.send(embed=text_module.embeds.embed_response("No keywords set.", "Nothing to display."))
    else:
        await message.channel.send(embed=text_module.embeds.embed_response("Keywords:", f"{keywords_list}"))


async def check_keywords(guild_id, message):
    guild_data = data.get_guild_data(guild_id)
    for keyword in guild_data["keywords"].keys():
        if message.content.__contains__(keyword):
            await message.channel.send(guild_data["keywords"][keyword][random.randint(0, len(guild_data["keywords"][keyword])-1)])
            return
